"""TokenSentry Skills package."""

from __future__ import annotations

# Import all skill modules to trigger registration
# Use explicit imports to avoid circular import issues
from tokensentry.skills import (
    agent_workflow,  # noqa: F401,E402
    analyzer,  # noqa: F401,E402
    context_engineer,  # noqa: F401,E402
    cost_analyst,  # noqa: F401,E402
    few_shot,  # noqa: F401,E402
    model_adapter,  # noqa: F401,E402
    optimizer,  # noqa: F401,E402
    prompt_documenter,  # noqa: F401,E402
    prompt_evaluator,  # noqa: F401,E402
    security_auditor,  # noqa: F401,E402
    skill_composer,  # noqa: F401,E402
    structured_output,  # noqa: F401,E402
    system_prompt_designer,  # noqa: F401,E402
    token_auditor,  # noqa: F401,E402
    validator_skill,  # noqa: F401,E402
)
from tokensentry.skills.base import BaseSkill, SkillContext, SkillRegistry, SkillResult, registry
from tokensentry.skills.composer import (
    COMPOSITION_PLANS,
    CompositionPlan,
    CompositionStep,
    SkillComposer,
)
from tokensentry.skills.loader import load_builtin_skills, load_skills_from_directory
from tokensentry.skills.validator import SkillValidator, validate_registry
from tokensentry.skills.validator_skill import ValidatorSkill

__all__ = [
    # Base
    "BaseSkill",
    "SkillContext",
    "SkillResult",
    "SkillRegistry",
    "registry",
    # Composer
    "CompositionPlan",
    "CompositionStep",
    "SkillComposer",
    "COMPOSITION_PLANS",
    # Loader
    "load_builtin_skills",
    "load_skills_from_directory",
    # Validator
    "SkillValidator",
    "validate_registry",
    # Skills
    "ValidatorSkill",
]