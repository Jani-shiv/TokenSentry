"""TokenSentry Skills package."""

from __future__ import annotations

from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, SkillRegistry, registry
from tokensentry.skills.composer import (
    CompositionPlan,
    CompositionStep,
    SkillComposer,
    COMPOSITION_PLANS,
)
from tokensentry.skills.loader import load_builtin_skills, load_skills_from_directory
from tokensentry.skills.validator import SkillValidator, validate_registry
from tokensentry.skills.validator_skill import ValidatorSkill

# Import all skill modules to trigger registration
# Use explicit imports to avoid circular import issues
from tokensentry.skills import analyzer  # noqa: F401,E402
from tokensentry.skills import optimizer  # noqa: F401,E402
from tokensentry.skills import token_auditor  # noqa: F401,E402
from tokensentry.skills import validator_skill  # noqa: F401,E402
from tokensentry.skills import context_engineer  # noqa: F401,E402
from tokensentry.skills import system_prompt_designer  # noqa: F401,E402
from tokensentry.skills import security_auditor  # noqa: F401,E402
from tokensentry.skills import structured_output  # noqa: F401,E402
from tokensentry.skills import few_shot  # noqa: F401,E402
from tokensentry.skills import agent_workflow  # noqa: F401,E402
from tokensentry.skills import model_adapter  # noqa: F401,E402
from tokensentry.skills import cost_analyst  # noqa: F401,E402
from tokensentry.skills import prompt_evaluator  # noqa: F401,E402
from tokensentry.skills import prompt_documenter  # noqa: F401,E402
from tokensentry.skills import skill_composer  # noqa: F401,E402

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