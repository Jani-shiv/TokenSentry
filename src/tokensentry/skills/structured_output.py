"""tokensentry-structured-output skill implementation."""

from __future__ import annotations

import json
from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry
from tokensentry.validation.schemas import (
    validate_json_structure,
    validate_yaml_structure,
    compare_structures,
    detect_output_format,
    extract_schema_from_prompt,
)


class StructuredOutputSkill(BaseSkill):
    """Optimize prompts that require structured outputs (JSON, YAML, XML, etc.)."""

    metadata = SkillMetadata(
        name="tokensentry-structured-output",
        version="0.1.0",
        description="Analyze and optimize prompts requiring structured output formats with schema preservation.",
        capabilities=[
            "JSON/YAML/XML output format requirement detection",
            "Schema extraction from prompt examples",
            "Schema preservation validation",
            "Field requirement analysis (required/optional, types, enums)",
            "Output format constraint optimization",
            "Schema-aware token optimization",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt requiring structured output"},
                "schema": {"type": "object", "description": "Optional explicit schema"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "detected_format": {"type": "string"},
                "extracted_schema": {"type": "object"},
                "field_requirements": {"type": "array"},
                "format_constraints": {"type": "array"},
                "optimization_suggestions": {"type": "array"},
                "schema_validation_errors": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer", "tokensentry-validator"],
        tags=["structured-output", "json", "yaml", "schema", "validation"],
        entry_point="structured_output.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute structured output analysis."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            explicit_schema = self.config.get("schema")

            # Analyze prompt
            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Detect output format
            detected_format = detect_output_format(context.prompt)

            # Extract schema from prompt
            extracted_schema = explicit_schema or extract_schema_from_prompt(context.prompt)

            # Analyze field requirements
            field_requirements = self._analyze_field_requirements(analysis, extracted_schema)

            # Identify format constraints
            format_constraints = self._analyze_format_constraints(analysis)

            # Generate optimization suggestions
            suggestions = self._generate_suggestions(analysis, detected_format, extracted_schema)

            output = {
                "detected_format": detected_format,
                "extracted_schema": extracted_schema,
                "field_requirements": field_requirements,
                "format_constraints": format_constraints,
                "optimization_suggestions": suggestions,
                "schema_validation_errors": [],
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

    def _analyze_field_requirements(self, analysis, schema: dict | None) -> list[dict]:
        """Analyze field requirements from schema and prompt."""
        fields = []

        if schema and "properties" in schema:
            for name, props in schema["properties"].items():
                fields.append({
                    "name": name,
                    "type": props.get("type"),
                    "required": name in schema.get("required", []),
                    "description": props.get("description"),
                    "enum": props.get("enum"),
                    "default": props.get("default"),
                })

        # Also check requirements from prompt
        for req in analysis.requirements:
            if req.type in ("format", "output", "schema"):
                # Could extract field names from requirement text
                pass

        return fields

    def _analyze_format_constraints(self, analysis) -> list[dict]:
        """Analyze format constraints from prompt."""
        constraints = []

        prompt_lower = analysis.prompt.lower() if hasattr(analysis, 'prompt') else ""

        if "json" in prompt_lower:
            constraints.append({"format": "json", "strict": "strict" in prompt_lower})
        if "yaml" in prompt_lower or "yml" in prompt_lower:
            constraints.append({"format": "yaml", "strict": "strict" in prompt_lower})
        if "xml" in prompt_lower:
            constraints.append({"format": "xml"})
        if "csv" in prompt_lower:
            constraints.append({"format": "csv"})
        if "markdown" in prompt_lower or "md" in prompt_lower:
            constraints.append({"format": "markdown"})

        return constraints

    def _generate_suggestions(self, analysis, detected_format: str | None, schema: dict | None) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []

        if not detected_format:
            suggestions.append("Add explicit output format requirement (JSON, YAML, etc.)")

        if schema and "required" in schema:
            req_count = len(schema["required"])
            if req_count > 10:
                suggestions.append(f"Consider reducing required fields ({req_count}) to improve reliability")

        # Check for redundancy in format specification
        format_mentions = sum(1 for req in analysis.requirements if req.type in ("format", "output", "schema"))
        if format_mentions > 1:
            suggestions.append("Consolidate multiple format requirements into single specification")

        # Suggest schema inclusion
        if detected_format and not schema:
            suggestions.append("Include explicit schema definition in prompt for better validation")

        return suggestions


# Register skill
registry.register(StructuredOutputSkill)