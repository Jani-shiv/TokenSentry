"""Validation package."""

from __future__ import annotations

from tokensentry.validation.diff import (
    ChangeClassifier,
    create_detailed_diff,
    format_diff_for_report,
)
from tokensentry.validation.preservation import (
    PreservationValidator,
    validate_prompt_enhanced,
)
from tokensentry.validation.schemas import (
    SchemaValidationError,
    compare_structures,
    detect_output_format,
    extract_schema_from_prompt,
    validate_json_structure,
    validate_yaml_structure,
)

__all__ = [
    # Preservation
    "PreservationValidator",
    "validate_prompt_enhanced",
    # Schemas
    "SchemaValidationError",
    "compare_structures",
    "detect_output_format",
    "extract_schema_from_prompt",
    "validate_json_structure",
    "validate_yaml_structure",
    # Diff
    "ChangeClassifier",
    "create_detailed_diff",
    "format_diff_for_report",
]