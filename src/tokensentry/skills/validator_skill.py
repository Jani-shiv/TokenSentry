"""tokensentry-validator skill implementation."""

from __future__ import annotations

from tokensentry.core.validator import validate_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class ValidatorSkill(BaseSkill):
    """Review an optimized prompt for missing or changed requirements."""

    metadata = SkillMetadata(
        name="tokensentry-validator",
        version="0.1.0",
        description="Validate optimized prompt against original for requirement preservation.",
        capabilities=[
            "Requirement preservation checking (positive/negative/value/format/schema)",
            "Technical literal byte-for-byte verification",
            "Negative constraint weakening detection",
            "Output schema/structure preservation validation",
            "Detailed change classification (exact/structural/probable/uncertain/modified/missing/weakened)",
            "Confidence scoring for each check",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "original_prompt": {"type": "string", "description": "Original prompt text"},
                "optimized_prompt": {"type": "string", "description": "Optimized prompt text"},
                "tokenizer": {"type": "string", "description": "Tokenizer used"},
            },
            "required": ["original_prompt", "optimized_prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "passed": {"type": "boolean"},
                "checks": {"type": "array"},
                "preserved_lines": {"type": "array"},
                "missing_lines": {"type": "array"},
                "modified_lines": {"type": "array"},
                "weakened_negatives": {"type": "array"},
                "warnings": {"type": "array"},
                "summary": {"type": "object"},
            },
        },
        dependencies=["tokensentry-analyzer", "tokensentry-optimizer"],
        tags=["validation", "preservation", "verification", "semantic"],
        entry_point="validator.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute validation."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: original_prompt and optimized_prompt required",
                )

            original = self.config.get("original_prompt", context.prompt)
            optimized = self.config.get("optimized_prompt")

            if not optimized:
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="optimized_prompt is required",
                )

            # Get requirements and literals from analysis if available
            original_requirements = None
            original_literals = None
            if context.analysis:
                original_requirements = context.analysis.requirements
                original_literals = context.analysis.technical_literals

            tokenizer = self.config.get("tokenizer")

            result = validate_prompt(
                original=original,
                optimized=optimized,
                original_requirements=original_requirements,
                original_literals=original_literals,
            )

            context.validation = result

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
registry.register(ValidatorSkill)