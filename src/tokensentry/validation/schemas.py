"""Schema validation for structured output preservation."""

from __future__ import annotations

import json
import re
from typing import Any

import yaml


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""

    def __init__(self, message: str, path: str = "", details: dict | None = None):
        super().__init__(message)
        self.path = path
        self.details = details or {}


def detect_output_format(prompt: str) -> str | None:
    """Detect expected output format from prompt."""
    prompt_lower = prompt.lower()

    if "json" in prompt_lower:
        return "json"
    if "yaml" in prompt_lower or "yml" in prompt_lower:
        return "yaml"
    if "xml" in prompt_lower:
        return "xml"
    if "csv" in prompt_lower:
        return "csv"
    if "markdown" in prompt_lower or "md" in prompt_lower:
        return "markdown"

    return None


def extract_schema_from_prompt(prompt: str) -> dict[str, Any] | None:
    """Extract JSON/YAML schema definition from prompt if present."""
    # Look for code fences with schema content
    schema_patterns = [
        (r"```(?:json|yaml|yml)\s*\n(.*?)\n```", "json"),
        (r"```(?:schema)\s*\n(.*?)\n```", "json"),
    ]

    for pattern, fmt in schema_patterns:
        match = re.search(pattern, prompt, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            try:
                if fmt == "json":
                    return json.loads(content)
                elif fmt == "yaml":
                    return yaml.safe_load(content)
            except Exception:
                pass

    return None


def validate_json_structure(data: str, schema: dict | None = None) -> list[SchemaValidationError]:
    """Validate JSON structure against optional schema."""
    errors: list[SchemaValidationError] = []

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        errors.append(SchemaValidationError(
            f"Invalid JSON: {e.msg}",
            path=f"line {e.lineno}, col {e.colno}",
            details={"doc": e.doc, "pos": e.pos}
        ))
        return errors

    if schema:
        errors.extend(_validate_against_schema(parsed, schema, ""))

    return errors


def validate_yaml_structure(data: str, schema: dict | None = None) -> list[SchemaValidationError]:
    """Validate YAML structure against optional schema."""
    errors: list[SchemaValidationError] = []

    try:
        parsed = yaml.safe_load(data)
    except yaml.YAMLError as e:
        errors.append(SchemaValidationError(
            f"Invalid YAML: {str(e)}",
            details={"error": str(e)}
        ))
        return errors

    if schema:
        errors.extend(_validate_against_schema(parsed, schema, ""))

    return errors


def _validate_against_schema(
    data: Any,
    schema: dict,
    path: str,
) -> list[SchemaValidationError]:
    """Validate data against a JSON schema-like definition."""
    errors: list[SchemaValidationError] = []

    # Type check
    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        expected = type_map.get(expected_type)
        if expected and not isinstance(data, expected):
            errors.append(SchemaValidationError(
                f"Expected type {expected_type}, got {type(data).__name__}",
                path=path,
            ))

    # Required fields for objects
    if isinstance(data, dict) and "required" in schema:
        for field in schema["required"]:
            if field not in data:
                errors.append(SchemaValidationError(
                    f"Missing required field: {field}",
                    path=f"{path}.{field}" if path else field,
                ))

    # Properties validation for objects
    if isinstance(data, dict) and "properties" in schema:
        for key, value in data.items():
            if key in schema["properties"]:
                errors.extend(_validate_against_schema(
                    value, schema["properties"][key], f"{path}.{key}" if path else key
                ))

    # Items validation for arrays
    if isinstance(data, list) and "items" in schema:
        for i, item in enumerate(data):
            errors.extend(_validate_against_schema(
                item, schema["items"], f"{path}[{i}]"
            ))

    # Enum validation
    if "enum" in schema and data not in schema["enum"]:
        errors.append(SchemaValidationError(
            f"Value not in allowed enum: {schema['enum']}",
            path=path,
        ))

    return errors


def compare_structures(original: str, optimized: str, format_hint: str | None = None) -> list[SchemaValidationError]:
    """Compare structure of two outputs."""
    errors: list[SchemaValidationError] = []

    fmt = format_hint or detect_output_format(original) or detect_output_format(optimized)

    if fmt == "json":
        orig_errors = validate_json_structure(original)
        opt_errors = validate_json_structure(optimized)
    elif fmt == "yaml":
        orig_errors = validate_yaml_structure(original)
        opt_errors = validate_yaml_structure(optimized)
    else:
        # Text comparison fallback
        return _compare_text_structure(original, optimized)

    # Check if both are valid
    if orig_errors and not opt_errors:
        errors.append(SchemaValidationError(
            "Original was valid but optimized is invalid",
            details={"original_errors": [str(e) for e in orig_errors]}
        ))
    elif not orig_errors and opt_errors:
        errors.append(SchemaValidationError(
            "Optimized introduced structural errors",
            details={"optimized_errors": [str(e) for e in opt_errors]}
        ))

    return errors


def _compare_text_structure(original: str, optimized: str) -> list[SchemaValidationError]:
    """Fallback text structure comparison."""
    errors: list[SchemaValidationError] = []

    orig_lines = [line.strip() for line in original.splitlines() if line.strip()]
    opt_lines = [line.strip() for line in optimized.splitlines() if line.strip()]

    # Check for major structural elements
    orig_has_headings = any(line.startswith("#") for line in orig_lines)
    opt_has_headings = any(line.startswith("#") for line in opt_lines)

    if orig_has_headings and not opt_has_headings:
        errors.append(SchemaValidationError(
            "Optimized output lost heading structure",
            details={"original_headings": sum(1 for line in orig_lines if line.startswith("#"))}
        ))

    orig_has_code = "```" in original
    opt_has_code = "```" in optimized

    if orig_has_code and not opt_has_code:
        errors.append(SchemaValidationError(
            "Optimized output lost code blocks",
        ))

    return errors