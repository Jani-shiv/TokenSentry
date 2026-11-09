"""Skill loader and discovery."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any

from tokensentry.skills.base import SkillRegistry, registry


def load_builtin_skills(skill_registry: SkillRegistry | None = None) -> SkillRegistry:
    """Load all builtin skills."""
    if skill_registry is None:
        skill_registry = registry

    # Import all skill modules to trigger registration
    from tokensentry.skills import (  # noqa: F401
        analyzer,
        auditor,
        composer,
        context_engineer,
        cost_analyst,
        documenter,
        evaluator,
        few_shot,
        model_adapter,
        optimizer,
        security_auditor,
        structured_output,
        system_prompt_designer,
        token_auditor,
        validator,
        workflow,
    )

    return skill_registry


def load_skills_from_directory(
    path: Path,
    skill_registry: SkillRegistry | None = None,
) -> SkillRegistry:
    """Load skills from a directory of Python modules."""
    if skill_registry is None:
        skill_registry = registry

    # Add directory to Python path
    import sys
    sys.path.insert(0, str(path.parent))

    for module_info in pkgutil.iter_modules([str(path)]):
        if module_info.name.startswith("tokensentry_") or module_info.name.startswith("skill_"):
            try:
                module = importlib.import_module(module_info.name)
                # Check for register_skills function
                if hasattr(module, "register_skills"):
                    module.register_skills(skill_registry)
            except Exception as e:
                print(f"Failed to load skill module {module_info.name}: {e}")

    return skill_registry


def discover_skill_metadata(skill_registry: SkillRegistry) -> dict[str, dict[str, Any]]:
    """Discover metadata for all registered skills."""
    metadata = {}
    for name in skill_registry.list_skills():
        skill_meta = skill_registry.get_metadata(name)
        if skill_meta:
            metadata[name] = skill_meta.model_dump()
    return metadata