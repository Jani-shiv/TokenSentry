"""Base classes for TokenSentry Skills."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from tokensentry.models import SkillMetadata


@dataclass
class SkillContext:
    """Context passed between skills in a composition."""

    prompt: str
    analysis: Any = None
    optimization: Any = None
    validation: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillResult:
    """Result from a skill execution."""

    skill_name: str
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseSkill(ABC):
    """Base class for all TokenSentry skills."""

    # Class-level metadata (must be overridden)
    metadata: SkillMetadata

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize skill with optional config."""
        self.config = config or {}

    @abstractmethod
    def execute(self, context: SkillContext) -> SkillResult:
        """Execute the skill with the given context."""
        pass

    def validate_input(self, context: SkillContext) -> bool:
        """Validate input context before execution."""
        return bool(context.prompt and context.prompt.strip())

    def get_metadata(self) -> SkillMetadata:
        """Get skill metadata."""
        return self.metadata


class SkillRegistry:
    """Registry for skill discovery and management."""

    def __init__(self) -> None:
        self._skills: dict[str, type[BaseSkill]] = {}
        self._instances: dict[str, BaseSkill] = {}

    def register(self, skill_class: type[BaseSkill]) -> None:
        """Register a skill class."""
        if not hasattr(skill_class, 'metadata'):
            raise ValueError(f"Skill {skill_class.__name__} missing metadata")
        name = skill_class.metadata.name
        if name in self._skills:
            raise ValueError(f"Skill already registered: {name}")
        self._skills[name] = skill_class

    def get(self, name: str) -> type[BaseSkill] | None:
        """Get skill class by name."""
        return self._skills.get(name)

    def get_instance(self, name: str, config: dict[str, Any] | None = None) -> BaseSkill | None:
        """Get or create skill instance."""
        if name not in self._instances:
            skill_class = self._skills.get(name)
            if skill_class:
                self._instances[name] = skill_class(config)
        return self._instances.get(name)

    def list_skills(self) -> list[str]:
        """List registered skill names."""
        return sorted(self._skills.keys())

    def get_metadata(self, name: str) -> SkillMetadata | None:
        """Get skill metadata by name."""
        skill_class = self._skills.get(name)
        if skill_class:
            return skill_class.metadata
        return None


# Global registry
registry = SkillRegistry()