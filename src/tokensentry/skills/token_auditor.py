"""tokensentry-token-auditor skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class TokenAuditorSkill(BaseSkill):
    """Audit token consumption and identify high-cost prompt sections."""

    metadata = SkillMetadata(
        name="tokensentry-token-auditor",
        version="0.1.0",
        description="Audit token consumption, identify high-cost sections, and estimate savings.",
        capabilities=[
            "Token counting with explicit tokenizer selection",
            "Section-level token breakdown",
            "Identify repeated context and oversized examples",
            "Estimate token savings from optimization",
            "Before/after token comparison",
            "Model-aware tokenizer selection",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt text to audit"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
                "target_model": {"type": "string", "description": "Target model for cost estimation"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "total_tokens": {"type": "integer"},
                "tokenizer": {"type": "object"},
                "section_breakdown": {"type": "array"},
                "repeated_sections": {"type": "array"},
                "savings_estimate": {"type": "object"},
                "cost_estimate": {"type": "object"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["tokens", "audit", "cost", "measurement"],
        entry_point="token_auditor.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute token audit."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Calculate section breakdown
            section_breakdown = []
            for section in analysis.sections:
                # Estimate tokens for each section
                tokens = len(section.content) // 4  # Rough estimate
                section_breakdown.append({
                    "type": section.type,
                    "title": section.title,
                    "lines": section.end_line - section.start_line + 1,
                    "estimated_tokens": tokens,
                    "percentage": round(tokens / analysis.token_count * 100, 1) if analysis.token_count > 0 else 0,
                })

            # Find repeated sections
            repeated = []
            section_texts = [s.content.strip() for s in analysis.sections if s.content.strip()]
            from collections import Counter
            for text, count in Counter(section_texts).items():
                if count > 1 and len(text) > 20:
                    repeated.append({
                        "content": text[:200],
                        "count": count,
                        "estimated_tokens": len(text) // 4,
                    })

            # Estimate savings
            savings = {
                "conservative": max(0, analysis.token_count // 20),  # ~5%
                "balanced": max(0, analysis.token_count // 10),      # ~10%
                "aggressive": max(0, analysis.token_count // 5),     # ~20%
            }

            output = {
                "total_tokens": analysis.token_count,
                "tokenizer": {
                    "name": analysis.tokenizer.name,
                    "exact": analysis.tokenizer.is_exact,
                },
                "section_breakdown": section_breakdown,
                "repeated_sections": repeated,
                "savings_estimate": savings,
                "cost_estimate": {
                    "note": "Actual cost depends on provider pricing, caching, and model",
                    "estimated_input_cost_usd_per_1k": 0.0015,  # Rough estimate
                },
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


# Register skill
registry.register(TokenAuditorSkill)