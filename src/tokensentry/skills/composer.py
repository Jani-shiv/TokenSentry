"""Skill composer for orchestrating multiple skills."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tokensentry.skills.base import SkillContext, SkillRegistry, SkillResult, registry


@dataclass
class CompositionStep:
    """Single step in a skill composition."""

    skill_name: str
    config: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    condition: str | None = None  # Optional condition to run this step


@dataclass
class CompositionPlan:
    """Plan for executing multiple skills in order."""

    name: str
    steps: list[CompositionStep]
    description: str = ""


class SkillComposer:
    """Orchestrate multiple skills in a defined sequence."""

    def __init__(self, skill_registry: SkillRegistry | None = None) -> None:
        self.registry = skill_registry or registry

    def execute_plan(
        self,
        plan: CompositionPlan,
        initial_context: SkillContext,
    ) -> dict[str, SkillResult]:
        """Execute a composition plan."""
        results: dict[str, SkillResult] = {}
        context = initial_context

        # Build dependency graph
        {step.skill_name: step for step in plan.steps}
        executed = set()

        def can_execute(step: CompositionStep) -> bool:
            return all(dep in executed for dep in step.depends_on)

        def check_condition(step: CompositionStep, ctx: SkillContext) -> bool:
            if not step.condition:
                return True
            # Simple condition evaluation (could be extended)
            return True

        # Execute steps respecting dependencies
        while len(executed) < len(plan.steps):
            progress = False
            for step in plan.steps:
                if step.skill_name in executed:
                    continue
                if not can_execute(step):
                    continue
                if not check_condition(step, context):
                    results[step.skill_name] = SkillResult(
                        skill_name=step.skill_name,
                        success=False,
                        error="Condition not met",
                    )
                    executed.add(step.skill_name)
                    continue

                # Get skill instance
                skill = self.registry.get_instance(step.skill_name, step.config)
                if not skill:
                    results[step.skill_name] = SkillResult(
                        skill_name=step.skill_name,
                        success=False,
                        error=f"Skill not found: {step.skill_name}",
                    )
                    executed.add(step.skill_name)
                    continue

                # Execute skill
                try:
                    result = skill.execute(context)
                    results[step.skill_name] = result

                    # Update context with result
                    if result.success and result.output:
                        context.metadata[step.skill_name] = result.output

                    executed.add(step.skill_name)
                    progress = True
                except Exception as e:
                    results[step.skill_name] = SkillResult(
                        skill_name=step.skill_name,
                        success=False,
                        error=str(e),
                    )
                    executed.add(step.skill_name)

            if not progress:
                # Circular dependency or other issue
                remaining = [s.skill_name for s in plan.steps if s.skill_name not in executed]
                for name in remaining:
                    results[name] = SkillResult(
                        skill_name=name,
                        success=False,
                        error="Circular dependency or unresolved dependency",
                    )
                break

        return results


# Predefined composition plans
STANDARD_ANALYSIS_PLAN = CompositionPlan(
    name="standard_analysis",
    description="Standard prompt analysis pipeline",
    steps=[
        CompositionStep(skill_name="tokensentry-analyzer"),
        CompositionStep(skill_name="tokensentry-token-auditor", depends_on=["tokensentry-analyzer"]),
        CompositionStep(skill_name="tokensentry-prompt-security-auditor", depends_on=["tokensentry-analyzer"]),
    ],
)

FULL_OPTIMIZATION_PLAN = CompositionPlan(
    name="full_optimization",
    description="Complete optimization with validation",
    steps=[
        CompositionStep(skill_name="tokensentry-analyzer"),
        CompositionStep(skill_name="tokensentry-token-auditor", depends_on=["tokensentry-analyzer"]),
        CompositionStep(skill_name="tokensentry-optimizer", depends_on=["tokensentry-analyzer", "tokensentry-token-auditor"]),
        CompositionStep(skill_name="tokensentry-validator", depends_on=["tokensentry-optimizer"]),
    ],
)

SECURITY_FOCUSED_PLAN = CompositionPlan(
    name="security_focused",
    description="Security-focused analysis",
    steps=[
        CompositionStep(skill_name="tokensentry-analyzer"),
        CompositionStep(skill_name="tokensentry-prompt-security-auditor", depends_on=["tokensentry-analyzer"]),
    ],
)

COMPOSITION_PLANS = {
    "standard": STANDARD_ANALYSIS_PLAN,
    "full": FULL_OPTIMIZATION_PLAN,
    "security": SECURITY_FOCUSED_PLAN,
}