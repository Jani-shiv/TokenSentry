"""tokensentry-optimizer skill implementation."""

from __future__ import annotations

from tokensentry.core.optimizer import optimize_prompt
from tokensentry.models import OptimizationProfile, SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class OptimizerSkill(BaseSkill):
    """Conservatively optimize prompts while preserving intent and constraints."""

    metadata = SkillMetadata(
        name="tokensentry-optimizer",
        version="0.1.0",
        description="Optimize prompts with configurable aggressiveness while preserving critical requirements.",
        capabilities=[
            "Conservative optimization (whitespace, exact duplicates)",
            "Balanced optimization (phrase consolidation, transition removal, bullet normalization)",
            "Aggressive optimization (filler removal, explanation compression, section reorganization)",
            "Technical literal preservation (code, commands, URLs, schemas, values)",
            "Transformation tracking with token delta",
            "Warning generation for risky transformations",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt text to optimize"},
                "profile": {"type": "string", "enum": ["conservative", "balanced", "aggressive"], "default": "conservative"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
                "technical_literals": {"type": "array", "description": "Pre-identified literals to preserve"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "original": {"type": "string"},
                "optimized": {"type": "string"},
                "profile": {"type": "string"},
                "tokenizer": {"type": "object"},
                "original_token_count": {"type": "integer"},
                "optimized_token_count": {"type": "integer"},
                "token_delta": {"type": "integer"},
                "token_reduction_pct": {"type": "number"},
                "transformations": {"type": "array"},
                "warnings": {"type": "array"},
                "preserved_literals": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["optimization", "transformation", "token-reduction"],
        entry_point="optimizer.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute prompt optimization."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            profile_str = self.config.get("profile", "conservative")
            profile = OptimizationProfile(profile_str)
            tokenizer = self.config.get("tokenizer")
            technical_literals = self.config.get("technical_literals")

            # Use literals from analysis if available
            if technical_literals is None and context.analysis:
                technical_literals = context.analysis.technical_literals

            result = optimize_prompt(
                prompt=context.prompt,
                profile=profile,
                tokenizer_name=tokenizer,
                technical_literals=technical_literals,
            )

            context.optimization = result

            return SkillResult(
                skill_name=self.metadata.name,
                success=True,
                output=result.model_dump(mode="json"),
            )
        except Exception as e:
            return SkillResult(
                skill_name=self.metadata.name,
                success=False,
                error=str(e),
            )


# Register skill
registry.register(OptimizerSkill)