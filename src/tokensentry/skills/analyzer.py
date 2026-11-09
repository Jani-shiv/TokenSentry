"""tokensentry-analyzer skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class AnalyzerSkill(BaseSkill):
    """Analyze prompt structure, clarity, redundancy, and token measurement metadata."""

    metadata = SkillMetadata(
        name="tokensentry-analyzer",
        version="0.1.0",
        description="Perform complete prompt analysis including structure, clarity, redundancy, and token measurement.",
        capabilities=[
            "Analyze prompt structure (headings, code fences, lists, tables)",
            "Extract requirements and constraints",
            "Identify technical literals (code, commands, URLs, schemas)",
            "Detect redundancy (duplicate lines, repeated phrases)",
            "Detect ambiguity (vague quantifiers, hedging, conditionals)",
            "Detect contradictions (conflicting requirements)",
            "Measure complexity (nesting depth, section count, density)",
            "Score quality (clarity, completeness, structure, conciseness, actionability)",
            "Token counting with explicit tokenizer selection",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt text to analyze"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use (default: character-estimate)"},
                "prompt_id": {"type": "string", "description": "Optional identifier for the prompt"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "prompt_id": {"type": "string"},
                "stats": {"type": "object"},
                "tokenizer": {"type": "object"},
                "token_count": {"type": "integer"},
                "sections": {"type": "array"},
                "requirements": {"type": "array"},
                "technical_literals": {"type": "array"},
                "findings": {"type": "array"},
                "quality_scores": {"type": "object"},
            },
        },
        dependencies=[],
        tags=["analysis", "structure", "quality", "tokens"],
        entry_point="analyzer.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute prompt analysis."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            prompt_id = self.config.get("prompt_id", "skill-analysis")

            analysis = analyze_prompt(
                prompt=context.prompt,
                tokenizer_name=tokenizer,
                prompt_id=prompt_id,
            )

            # Store in context for downstream skills
            context.analysis = analysis

            return SkillResult(
                skill_name=self.metadata.name,
                success=True,
                output=analysis.model_dump(mode="json"),
            )
        except Exception as e:
            return SkillResult(
                skill_name=self.metadata.name,
                success=False,
                error=str(e),
            )


# Register skill
registry.register(AnalyzerSkill)