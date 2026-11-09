"""Skill metadata validation."""

from __future__ import annotations

from tokensentry.models import SkillMetadata
from tokensentry.skills.base import SkillRegistry


class SkillValidator:
    """Validate skill metadata against specification."""

    REQUIRED_FIELDS = [
        "name",
        "version",
        "description",
        "capabilities",
        "input_schema",
        "output_schema",
    ]

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, metadata: SkillMetadata) -> bool:
        """Validate skill metadata."""
        self.errors = []
        self.warnings = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            value = getattr(metadata, field, None)
            if value is None:
                self.errors.append(f"Missing required field: {field}")

        # Validate name format
        if metadata.name:
            if not metadata.name.startswith("tokensentry-"):
                self.errors.append(f"Skill name must start with 'tokensentry-': {metadata.name}")

        # Validate version format (semver)
        if metadata.version:
            if not self._is_valid_version(metadata.version):
                self.warnings.append(f"Version should follow semver: {metadata.version}")

        # Check capabilities
        if metadata.capabilities:
            if not isinstance(metadata.capabilities, list):
                self.errors.append("Capabilities must be a list")
            elif len(metadata.capabilities) == 0:
                self.warnings.append("No capabilities declared")

        # Check input/output schemas
        if metadata.input_schema and not isinstance(metadata.input_schema, dict):
            self.errors.append("input_schema must be a dict")
        if metadata.output_schema and not isinstance(metadata.output_schema, dict):
            self.errors.append("output_schema must be a dict")

        # Check dependencies
        if metadata.dependencies:
            for dep in metadata.dependencies:
                if not dep.startswith("tokensentry-"):
                    self.warnings.append(f"Dependency should be tokensentry skill: {dep}")

        return len(self.errors) == 0

    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semver."""
        import re
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$"
        return bool(re.match(semver_pattern, version))

    def get_errors(self) -> list[str]:
        return self.errors

    def get_warnings(self) -> list[str]:
        return self.warnings


def validate_registry(skill_registry: SkillRegistry) -> dict[str, dict[str, object]]:
    """Validate all skills in a registry."""
    results = {}
    validator = SkillValidator()

    for name in skill_registry.list_skills():
        metadata = skill_registry.get_metadata(name)
        if metadata:
            is_valid = validator.validate(metadata)
            results[name] = {
                "valid": is_valid,
                "errors": validator.get_errors(),
                "warnings": validator.get_warnings(),
            }

    return results