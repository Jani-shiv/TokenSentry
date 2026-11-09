"""tokensentry-cost-analyst skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class CostAnalystSkill(BaseSkill):
    """Analyze potential AI API usage costs for prompts."""

    metadata = SkillMetadata(
        name="tokensentry-cost-analyst",
        version="0.1.0",
        description="Estimate API costs for prompts across different providers and models.",
        capabilities=[
            "Input token cost analysis with explicit tokenizer",
            "Output token estimation based on prompt type",
            "Multi-provider pricing comparison (OpenAI, Anthropic, etc.)",
            "Cached input token distinction where supported",
            "Scenario comparison (single vs batch vs streaming)",
            "Cost optimization recommendations",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to analyze"},
                "models": {"type": "array", "items": {"type": "string"}, "description": "Models to estimate for"},
                "output_tokens_estimate": {"type": "integer", "description": "Expected output tokens"},
                "requests_per_month": {"type": "integer", "default": 1000, "description": "Monthly request volume"},
                "use_cached_input": {"type": "boolean", "default": False, "description": "Whether input can be cached"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "input_tokens": {"type": "integer"},
                "estimated_output_tokens": {"type": "integer"},
                "per_request_cost": {"type": "object"},
                "monthly_cost_estimate": {"type": "object"},
                "cost_breakdown": {"type": "object"},
                "optimization_suggestions": {"type": "array"},
                "disclaimer": {"type": "string"},
            },
        },
        dependencies=["tokensentry-analyzer", "tokensentry-token-auditor"],
        tags=["cost", "pricing", "estimation", "budget", "api"],
        entry_point="cost_analyst.py",
        min_tokensentry_version="0.1.0",
    )

    # Rough pricing per 1K tokens (USD) - update regularly
    PRICING = {
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06, "cached_input": 0.015},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03, "cached_input": 0.005},
            "gpt-4o": {"input": 0.005, "output": 0.015, "cached_input": 0.0025},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "cached_input": 0.00025},
        },
        "anthropic": {
            "claude-3-opus": {"input": 0.015, "output": 0.075, "cached_input": 0.0075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015, "cached_input": 0.0015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125, "cached_input": 0.000125},
        },
        "google": {
            "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105, "cached_input": 0.00175},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003, "cached_input": 0.0000375},
        },
    }

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute cost analysis."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            models = self.config.get("models", ["gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet"])
            output_tokens = self.config.get("output_tokens_estimate", 500)
            requests = self.config.get("requests_per_month", 1000)
            cached = self.config.get("use_cached_input", False)

            analysis = analyze_prompt(context.prompt, tokenizer_name="character-estimate")
            input_tokens = analysis.token_count

            # Calculate costs per model
            per_request = {}
            monthly = {}

            for model in models:
                provider = self._get_provider(model)
                if provider not in self.PRICING or model not in self.PRICING[provider]:
                    per_request[model] = {"error": "Unknown model pricing"}
                    continue

                pricing = self.PRICING[provider][model]
                input_rate = pricing["cached_input"] if cached else pricing["input"]

                input_cost = (input_tokens / 1000) * input_rate
                output_cost = (output_tokens / 1000) * pricing["output"]
                total_per_request = input_cost + output_cost

                per_request[model] = {
                    "input_cost_usd": round(input_cost, 6),
                    "output_cost_usd": round(output_cost, 6),
                    "total_cost_usd": round(total_per_request, 6),
                    "provider": provider,
                }

                monthly[model] = {
                    "estimated_monthly_usd": round(total_per_request * requests, 2),
                    "requests": requests,
                }

            # Cost breakdown
            breakdown = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_input": cached,
                "requests_per_month": requests,
            }

            # Optimization suggestions
            suggestions = self._generate_suggestions(input_tokens, output_tokens, models, cached)

            output = {
                "input_tokens": input_tokens,
                "estimated_output_tokens": output_tokens,
                "per_request_cost": per_request,
                "monthly_cost_estimate": monthly,
                "cost_breakdown": breakdown,
                "optimization_suggestions": suggestions,
                "disclaimer": "Prices are estimates based on publicly available pricing as of 2024. Actual costs may vary. Check provider pricing pages for current rates.",
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

    def _get_provider(self, model: str) -> str:
        model_lower = model.lower()
        if any(m in model_lower for m in ["gpt-4", "gpt-3.5"]):
            return "openai"
        if "claude" in model_lower:
            return "anthropic"
        if "gemini" in model_lower:
            return "google"
        return "openai"  # default

    def _generate_suggestions(self, input_tokens: int, output_tokens: int, models: list[str], cached: bool) -> list[str]:
        suggestions = []

        if input_tokens > 10000:
            suggestions.append("Consider prompt compression - input tokens exceed 10K")

        if output_tokens > 2000:
            suggestions.append("Add output token limit to control costs")

        if not cached and input_tokens > 1000:
            suggestions.append("Enable prompt caching (if provider supports) for repeated inputs")

        # Compare model costs
        if "gpt-4" in str(models) and "gpt-3.5" in str(models):
            suggestions.append("Consider gpt-3.5-turbo for non-critical tasks (significantly cheaper)")

        if "claude-3-opus" in str(models):
            suggestions.append("Consider claude-3-sonnet for most tasks (lower cost, similar capability)")

        return suggestions


# Register skill
registry.register(CostAnalystSkill)