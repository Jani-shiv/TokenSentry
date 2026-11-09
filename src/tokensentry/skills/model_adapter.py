"""tokensentry-model-adapter skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry
from tokensentry.tokenizers import list_tokenizers, get_tokenizer


class ModelAdapterSkill(BaseSkill):
    """Adapt prompts for different model families and tokenizers."""

    metadata = SkillMetadata(
        name="tokensentry-model-adapter",
        version="0.1.0",
        description="Adapt prompts for different model families with tokenizer awareness and format compatibility.",
        capabilities=[
            "Model-specific tokenizer selection and token counting",
            "Context window awareness and truncation guidance",
            "Prompt format compatibility (chat templates, instruction formats)",
            "Model-specific instruction considerations (system prompts, roles)",
            "Cross-model token comparison",
            "Model capability alignment checking",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to adapt"},
                "target_models": {"type": "array", "items": {"type": "string"}, "description": "Target model names"},
                "source_model": {"type": "string", "description": "Source model (for comparison)"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "token_counts": {"type": "object"},
                "format_compatibility": {"type": "object"},
                "context_window_warnings": {"type": "array"},
                "instruction_adaptations": {"type": "array"},
                "cross_model_comparison": {"type": "object"},
            },
        },
        dependencies=["tokensentry-analyzer", "tokensentry-token-auditor"],
        tags=["model-adapter", "tokenizer", "cross-model", "compatibility"],
        entry_point="model_adapter.py",
        min_tokensentry_version="0.1.0",
    )

    # Model context windows (approximate)
    MODEL_CONTEXTS = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "claude-3-opus": 200000,
        "claude-3-sonnet": 200000,
        "claude-3-haiku": 200000,
        "llama-2-7b": 4096,
        "llama-2-13b": 4096,
        "llama-2-70b": 4096,
        "llama-3-8b": 8192,
        "llama-3-70b": 8192,
        "mistral-7b": 8192,
        "mixtral-8x7b": 32768,
        "gemma-7b": 8192,
        "gemma-2b": 8192,
    }

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute model adaptation analysis."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            target_models = self.config.get("target_models", ["gpt-4", "claude-3-sonnet", "llama-3-70b"])
            source_model = self.config.get("source_model")

            analysis = analyze_prompt(context.prompt, tokenizer_name="character-estimate")

            # Calculate token counts for each model
            token_counts = {}
            for model in target_models:
                tokenizer = self._get_tokenizer_for_model(model)
                if tokenizer:
                    count = tokenizer.count(context.prompt)
                    token_counts[model] = {
                        "tokens": count,
                        "tokenizer": tokenizer.name,
                        "context_window": self.MODEL_CONTEXTS.get(model, "unknown"),
                        "utilization_pct": round(count / self.MODEL_CONTEXTS.get(model, 1) * 100, 1) if self.MODEL_CONTEXTS.get(model) else "unknown",
                    }

            # Check context window utilization
            context_warnings = []
            for model, data in token_counts.items():
                if isinstance(data["context_window"], int) and isinstance(data["utilization_pct"], (int, float)):
                    if data["utilization_pct"] > 90:
                        context_warnings.append(f"{model}: {data['utilization_pct']}% context used - consider truncation")
                    elif data["utilization_pct"] > 70:
                        context_warnings.append(f"{model}: {data['utilization_pct']}% context used - monitor")

            # Format compatibility
            format_compat = self._check_format_compatibility(target_models)

            # Instruction adaptations
            adaptations = self._suggest_instruction_adaptations(target_models)

            # Cross-model comparison
            comparison = self._compare_models(token_counts, source_model)

            output = {
                "token_counts": token_counts,
                "format_compatibility": format_compat,
                "context_window_warnings": context_warnings,
                "instruction_adaptations": adaptations,
                "cross_model_comparison": comparison,
            }

            return SkillResult(
                skill_name=self.metadata.name,
                success=True,
                output=output,
            )
        except Exception as e:
            return SkillResult(
                skill_name=self.metadata.name,
                success=False,
                error=str(e),
            )

    def _get_tokenizer_for_model(self, model: str):
        """Get appropriate tokenizer for model."""
        model_lower = model.lower()

        # Map models to tokenizers
        if any(m in model_lower for m in ["gpt-4", "gpt-3.5", "gpt-4o", "gpt-4-turbo"]):
            return get_tokenizer("tiktoken:cl100k_base")
        if "claude" in model_lower:
            return get_tokenizer("character-estimate")  # Anthropic uses different tokenizer
        if "llama" in model_lower or "mistral" in model_lower or "mixtral" in model_lower or "gemma" in model_lower:
            return get_tokenizer("character-estimate")  # Would need HF tokenizer

        return get_tokenizer("character-estimate")

    def _check_format_compatibility(self, models: list[str]) -> dict:
        """Check prompt format compatibility across models."""
        compat = {}
        for model in models:
            model_lower = model.lower()
            compat[model] = {
                "supports_system_prompt": "gpt" in model_lower or "claude" in model_lower,
                "supports_function_calling": "gpt-4" in model_lower or "gpt-3.5" in model_lower,
                "chat_template": "chatml" if "gpt" in model_lower else "llama" if "llama" in model_lower else "default",
                "max_tokens_output": 4096 if "gpt-4" in model_lower else 2048,
            }
        return compat

    def _suggest_instruction_adaptations(self, models: list[str]) -> list[str]:
        """Suggest model-specific instruction adaptations."""
        adaptations = []

        for model in models:
            model_lower = model.lower()
            if "gpt" in model_lower:
                adaptations.append(f"{model}: Use explicit system prompt; leverage function calling if available")
            elif "claude" in model_lower:
                adaptations.append(f"{model}: Use XML tags for structure; avoid role-play in system prompt")
            elif "llama" in model_lower or "mistral" in model_lower:
                adaptations.append(f"{model}: Use <<SYS>> tags; keep instructions concise")
            else:
                adaptations.append(f"{model}: Use clear, explicit instructions; avoid model-specific syntax")

        return adaptations

    def _compare_models(self, token_counts: dict, source_model: str | None) -> dict:
        """Compare token counts across models."""
        comparison = {
            "models_compared": list(token_counts.keys()),
            "token_range": {
                "min": min(d["tokens"] for d in token_counts.values()),
                "max": max(d["tokens"] for d in token_counts.values()),
            },
        }

        if source_model and source_model in token_counts:
            source_tokens = token_counts[source_model]["tokens"]
            comparison["relative_to_source"] = {
                model: {
                    "ratio": round(d["tokens"] / source_tokens, 2) if source_tokens > 0 else "N/A",
                    "difference": d["tokens"] - source_tokens,
                }
                for model, d in token_counts.items()
            }

        return comparison


# Register skill
registry.register(ModelAdapterSkill)