"""Prompt validator for semantic preservation checking."""

from __future__ import annotations

from tokensentry.models import (
    PreservationStatus,
    Requirement,
    TechnicalLiteral,
    ValidationReport,
)
from tokensentry.validation import (
    PreservationValidator,
    validate_prompt_enhanced,
)


def validate_prompt(
    original: str,
    optimized: str,
    original_requirements: list[Requirement] | None = None,
    original_literals: list[TechnicalLiteral] | None = None,
) -> ValidationReport:
    """Validate optimized prompt against original for requirement preservation.

    Args:
        original: Original prompt text
        optimized: Optimized prompt text
        original_requirements: Pre-extracted requirements from original
        original_literals: Pre-identified technical literals from original

    Returns:
        Validation report with detailed checks
    """
    # Use enhanced validation
    checks = validate_prompt_enhanced(
        original,
        optimized,
        original_requirements,
        original_literals,
    )

    # Categorize results
    preserved_lines: list[str] = []
    missing_lines: list[str] = []
    modified_lines: list[str] = []
    weakened_negatives: list[str] = []

    for check in checks:
        if check.status == PreservationStatus.EXACT:
            preserved_lines.append(check.requirement.text)
        elif check.status == PreservationStatus.MISSING:
            missing_lines.append(check.requirement.text)
        elif check.status == PreservationStatus.MODIFIED:
            modified_lines.append(check.requirement.text)
        elif check.status == PreservationStatus.WEAKENED:
            weakened_negatives.append(check.requirement.text)
        else:
            # STRUCTURAL, PROBABLE, UNCERTAIN count as preserved
            preserved_lines.append(check.requirement.text)

    # Determine overall pass/fail
    failed = any(
        c.status in (PreservationStatus.MISSING, PreservationStatus.WEAKENED)
        for c in checks
    )
    passed = not failed

    # Build summary
    summary = {
        "total_checks": len(checks),
        "exact": sum(1 for c in checks if c.status == PreservationStatus.EXACT),
        "structural": sum(1 for c in checks if c.status == PreservationStatus.STRUCTURAL),
        "probable": sum(1 for c in checks if c.status == PreservationStatus.PROBABLE),
        "uncertain": sum(1 for c in checks if c.status == PreservationStatus.UNCERTAIN),
        "missing": sum(1 for c in checks if c.status == PreservationStatus.MISSING),
        "modified": sum(1 for c in checks if c.status == PreservationStatus.MODIFIED),
        "weakened": sum(1 for c in checks if c.status == PreservationStatus.WEAKENED),
    }

    # Add warnings
    warnings: list[str] = []
    if summary["missing"] > 0:
        warnings.append(f"{summary['missing']} requirements or literals missing from optimized prompt")
    if summary["weakened"] > 0:
        warnings.append(f"{summary['weakened']} negative constraints weakened")
    if summary["modified"] > 0:
        warnings.append(f"{summary['modified']} requirements modified")
    if not warnings:
        warnings.append("All critical requirements preserved. Human review still recommended.")

    return ValidationReport(
        passed=passed,
        checks=checks,
        preserved_lines=preserved_lines,
        missing_lines=missing_lines,
        modified_lines=modified_lines,
        weakened_negatives=weakened_negatives,
        warnings=warnings,
        summary=summary,
    )


# Re-export for backward compatibility
__all__ = ["validate_prompt", "PreservationValidator", "validate_prompt_enhanced"]