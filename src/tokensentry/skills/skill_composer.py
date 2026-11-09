"""tokensentry-skill-composer skill implementation."""

from __future__ import annotations

from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry
from tokensentry.skills.composer import COMPOSITION_PLANS, SkillComposer


class SkillComposerSkill(BaseSkill):
    """Combine multiple TokenSentry skills into a unified workflow."""

    metadata = SkillMetadata(
        name="tokensentry-skill-composer",
        version="0.1.0",
        description="Orchestrate multiple TokenSentry skills into a unified workflow with dependency resolution.",
        capabilities=[
            "Select relevant skills for a given task",
            "Define execution order with dependency resolution",
            "Pass structured results between skills",
            "Avoid conflicting transformations",
            "Generate unified report from multiple skills",
            "Support predefined and custom compositions",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to process"},
                "plan": {"type": "string", "enum": list(COMPOSITION_PLANS.keys()) + ["custom"], "description": "Composition plan to execute"},
                "custom_steps": {"type": "array", "description": "Custom composition steps (if plan=custom)"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "plan_executed": {"type": "string"},
                "skill_results": {"type": "object"},
                "unified_report": {"type": "object"},
                "execution_summary": {"type": "object"},
            },
        },
        dependencies=[],
        tags=["composition", "orchestration", "workflow", "multi-skill"],
        entry_point="skill_composer.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute skill composition."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            plan_name = self.config.get("plan", "standard")
            custom_steps = self.config.get("custom_steps", [])
            tokenizer = self.config.get("tokenizer")

            composer = SkillComposer(registry)

            if plan_name == "custom" and custom_steps:
                # Build custom plan
                from tokensentry.skills.composer import CompositionPlan, CompositionStep
                plan = CompositionPlan(
                    name="custom",
                    steps=[CompositionStep(**step) for step in custom_steps],
                    description="Custom composition",
                )
            else:
                plan = COMPOSITION_PLANS.get(plan_name, COMPOSITION_PLANS["standard"])

            # Prepare initial context with tokenizer info
            initial_context = SkillContext(
                prompt=context.prompt,
                metadata={"tokenizer": tokenizer, "plan": plan_name},
            )

            # Execute plan
            results = composer.execute_plan(plan, initial_context)

            # Build unified report
            unified = self._build_unified_report(results, plan)

            # Execution summary
            summary = {
                "plan": plan_name,
                "total_skills": len(plan.steps),
                "successful": sum(1 for r in results.values() if r.success),
                "failed": sum(1 for r in results.values() if not r.success),
                "errors": [r.error for r in results.values() if r.error],
            }

            def _serialize_result(r):
                return {
                    "skill_name": r.skill_name,
                    "success": r.success,
                    "output": r.output,
                    "error": r.error,
                    "metadata": r.metadata,
                }

            output = {
                "plan_executed": plan_name,
                "skill_results": {k: _serialize_result(v) for k, v in results.items()},
                "unified_report": unified,
                "execution_summary": summary,
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

    def _build_unified_report(self, results: dict, plan) -> dict:
        """Build unified report from skill results."""
        unified = {
            "analysis": None,
            "optimization": None,
            "validation": None,
            "audit": None,
            "cost": None,
            "security": None,
        }

        for skill_name, result in results.items():
            if not result.success:
                continue

            output = result.output
            if not output:
                continue

            if skill_name == "tokensentry-analyzer":
                unified["analysis"] = output
            elif skill_name == "tokensentry-optimizer":
                unified["optimization"] = output
            elif skill_name == "tokensentry-validator":
                unified["validation"] = output
            elif skill_name == "tokensentry-token-auditor":
                unified["audit"] = output
            elif skill_name == "tokensentry-cost-analyst":
                unified["cost"] = output
            elif skill_name == "tokensentry-security-auditor":
                unified["security"] = output
            elif skill_name == "tokensentry-prompt-security-auditor":
                unified["security"] = output
            # Add other skills as needed

        # Add cross-skill insights
        unified["insights"] = self._generate_insights(unified)

        return unified

    def _generate_insights(self, unified: dict) -> list[str]:
        """Generate cross-skill insights."""
        insights = []

        analysis = unified.get("analysis")
        optimization = unified.get("optimization")
        validation = unified.get("validation")

        if analysis and optimization:
            token_delta = optimization.get("token_delta", 0)
            if token_delta > 0:
                insights.append(f"Optimization saved {token_delta} tokens ({optimization.get('token_reduction_pct', 0):.1f}%)")

        if validation and not validation.get("passed", True):
            missing = len(validation.get("missing_lines", []))
            weakened = len(validation.get("weakened_negatives", []))
            if missing > 0:
                insights.append(f"Validation: {missing} requirements missing after optimization")
            if weakened > 0:
                insights.append(f"Validation: {weakened} negative constraints weakened")

        audit = unified.get("audit")
        if audit:
            repeated = audit.get("repeated_sections", [])
            if repeated:
                insights.append(f"Token audit: {len(repeated)} repeated sections found")

        cost = unified.get("cost")
        if cost:
            monthly = cost.get("monthly_cost_estimate", {})
            if monthly:
                min_cost = min(v.get("estimated_monthly_usd", float("inf")) for v in monthly.values())
                max_cost = max(v.get("estimated_monthly_usd", 0) for v in monthly.values())
                insights.append(f"Cost range: ${min_cost:.2f} - ${max_cost:.2f}/month across models")

        return insights


# Register skill
registry.register(SkillComposerSkill)