"""Prompt validator for semantic preservation checking."""

from __future__ import annotations

import difflib
import re

from tokensentry.models import (
    PreservationStatus,
    Requirement,
    TechnicalLiteral,
    ValidationCheck,
    ValidationReport,
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
    # Extract requirements if not provided
    if original_requirements is None:
        original_requirements = _extract_requirements(original)

    if original_literals is None:
        original_literals = _find_technical_literals(original)

    checks: list[ValidationCheck] = []
    preserved_lines: list[str] = []
    missing_lines: list[str] = []
    modified_lines: list[str] = []
    weakened_negatives: list[str] = []
    warnings: list[str] = []

    # 1. Check requirement preservation
    for req in original_requirements:
        check = _check_requirement(req, optimized)
        checks.append(check)

        if check.status == PreservationStatus.MISSING:
            missing_lines.append(req.text)
        elif check.status == PreservationStatus.MODIFIED:
            modified_lines.append(req.text)
        elif check.status == PreservationStatus.WEAKENED:
            weakened_negatives.append(req.text)
        else:
            preserved_lines.append(req.text)

    # 2. Check technical literal preservation
    for lit in original_literals:
        check = _check_literal(lit, optimized)
        checks.append(check)

        if check.status == PreservationStatus.MISSING:
            missing_lines.append(f"[{lit.type}] {lit.value}")
        elif check.status in (PreservationStatus.MODIFIED, PreservationStatus.WEAKENED):
            modified_lines.append(f"[{lit.type}] {lit.value}")
        else:
            preserved_lines.append(f"[{lit.type}] {lit.value}")

    # 3. Check negative constraint weakening
    negative_checks = _check_negative_constraints(original, optimized)
    for check in negative_checks:
        checks.append(check)
        if check.status == PreservationStatus.WEAKENED:
            weakened_negatives.append(check.requirement.text)

    # 4. Line-by-line comparison for structural changes
    line_checks = _compare_lines(original, optimized)
    for check in line_checks:
        checks.append(check)

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
    if summary["missing"] > 0:
        msg = f"{summary['missing']} requirements or literals missing from optimized prompt"
        warnings.append(msg)
    if summary["weakened"] > 0:
        msg = f"{summary['weakened']} negative constraints weakened"
        warnings.append(msg)
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


def _extract_requirements(text: str) -> list[Requirement]:
    """Extract requirements from text (simplified version)."""
    requirements: list[Requirement] = []
    lines = text.splitlines()

    patterns = [
        (r"\b(must|shall|required to|have to)\b", "positive"),
        (r"\b(must not|shall not|never|do not|don't|prohibited|forbidden)\b", "negative"),
        (
            r"\b(maximum|minimum|at most|at least|exactly|no more than|no less than)\s+(\d+)",
            "value",
        ),
        (r"\b(json|yaml|xml|csv|markdown|html)\b", "format"),
        (r"\b(output|return|respond|format|structure)\s+(as|in|with)\b", "output"),
        (r"\b(schema|specification|contract|interface)\b", "schema"),
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower:
            continue

        for pattern, req_type in patterns:
            for _match in re.finditer(pattern, line_lower, re.IGNORECASE):
                req = Requirement(
                    text=line.strip(),
                    type=req_type,  # type: ignore[arg-type]
                    line_range=(i + 1, i + 1),
                    is_critical=req_type in ("negative", "value"),
                )
                if req_type == "value":
                    value_match = re.search(r"(\d+)", line)
                    if value_match:
                        req.exact_value = value_match.group(1)
                requirements.append(req)

    # Deduplicate
    seen: set[str] = set()
    unique: list[Requirement] = []
    for req in requirements:
        key = f"{req.type}:{req.text[:100]}"
        if key not in seen:
            seen.add(key)
            unique.append(req)

    return unique


def _find_technical_literals(text: str) -> list[TechnicalLiteral]:
    """Find technical literals (simplified version)."""
    literals: list[TechnicalLiteral] = []
    lines = text.splitlines()

    patterns = [
        (r"`([^`\n]{3,})`", "code"),
        (
            r"\b(?:kubectl|docker|git|npm|pip|python|node|curl|wget|ssh|scp|rsync|terraform|ansible|helm)\S*",
            "command",
        ),
        (r"https?://[^\s\"'<>\)]+", "url"),
        (r"(?:[~/]|\.\./|\./)[\w\-./]+", "file_path"),
        (r"\{[^{}]*\}", "json"),
        (r"^\s*[\w\-]+:\s*\S+", "yaml"),
        (r"\$\{?[A-Z_][A-Z0-9_]*\}?", "variable"),
    ]

    for i, line in enumerate(lines):
        for pattern, lit_type in patterns:
            for match in re.finditer(pattern, line):
                value = match.group(0)
                if len(value) < 3:
                    continue
                literals.append(
                    TechnicalLiteral(
                        type=lit_type,  # type: ignore[arg-type]
                        value=value,
                        line_range=(i + 1, i + 1),
                        preservation_priority=(
                            10
                            if lit_type in ("command", "url", "file_path", "json", "yaml")
                            else 6
                        ),
                    )
                )

    seen: set[str] = set()
    unique: list[TechnicalLiteral] = []
    for lit in literals:
        key = f"{lit.type}:{lit.value}"
        if key not in seen:
            seen.add(key)
            unique.append(lit)

    return unique


def _check_requirement(req: Requirement, optimized: str) -> ValidationCheck:
    """Check if a requirement is preserved in optimized text."""
    req_text = req.text.strip()
    req_lower = req_text.lower()
    optimized_lower = optimized.lower()

    # Exact match
    if req_text in optimized:
        return ValidationCheck(
            requirement=req,
            status=PreservationStatus.EXACT,
            evidence=req_text,
            optimized_text=req_text,
            confidence=1.0,
        )

    # Check for key terms
    key_terms = _extract_key_terms(req_text)
    if key_terms:
        matches = sum(1 for term in key_terms if term.lower() in optimized_lower)
        ratio = matches / len(key_terms)

        if ratio >= 0.9:
            return ValidationCheck(
                requirement=req,
                status=PreservationStatus.STRUCTURAL,
                evidence=f"Key terms preserved: {matches}/{len(key_terms)}",
                confidence=0.9,
            )
        elif ratio >= 0.7:
            return ValidationCheck(
                requirement=req,
                status=PreservationStatus.PROBABLE,
                evidence=f"Most key terms preserved: {matches}/{len(key_terms)}",
                confidence=0.7,
            )
        elif ratio >= 0.5:
            return ValidationCheck(
                requirement=req,
                status=PreservationStatus.UNCERTAIN,
                evidence=f"Partial key terms preserved: {matches}/{len(key_terms)}",
                confidence=0.5,
            )

    # For negative constraints, check specifically
    if req.type == "negative":
        neg_terms = [
            "not", "never", "no", "don't", "must not",
            "shall not", "prohibited", "forbidden",
        ]
        has_negation = any(term in req_lower for term in neg_terms)
        if has_negation:
            opt_has_negation = any(term in optimized_lower for term in neg_terms)
            if not opt_has_negation:
                return ValidationCheck(
                    requirement=req,
                    status=PreservationStatus.WEAKENED,
                    evidence="Negative constraint appears to be weakened or removed",
                    confidence=0.8,
                    notes="Negative instruction may have been dropped during optimization",
                )

    return ValidationCheck(
        requirement=req,
        status=PreservationStatus.MISSING,
        evidence="Requirement not found in optimized prompt",
        confidence=0.9,
    )


def _check_literal(lit: TechnicalLiteral, optimized: str) -> ValidationCheck:
    """Check if a technical literal is preserved."""
    req = Requirement(
        text=f"[{lit.type}] {lit.value}",
        type="value",
        is_critical=lit.preservation_priority >= 8,
    )

    if lit.value in optimized:
        return ValidationCheck(
            requirement=req,
            status=PreservationStatus.EXACT,
            evidence=lit.value,
            optimized_text=lit.value,
            confidence=1.0,
        )

    # Fuzzy match for code/commands
    if lit.type in ("code", "command", "json", "yaml"):
        # Check if similar content exists
        matcher = difflib.SequenceMatcher(None, lit.value, optimized)
        match = matcher.find_longest_match(0, len(lit.value), 0, len(optimized))
        if match.size >= len(lit.value) * 0.8:
            return ValidationCheck(
                requirement=req,
                status=PreservationStatus.STRUCTURAL,
                evidence=f"Similar content found ({match.size}/{len(lit.value)} chars)",
                confidence=0.8,
            )

    return ValidationCheck(
        requirement=req,
        status=PreservationStatus.MISSING,
        evidence=f"Literal not found: {lit.value[:100]}",
        confidence=0.9,
    )


def _check_negative_constraints(original: str, optimized: str) -> list[ValidationCheck]:
    """Specifically check negative constraint preservation."""
    checks: list[ValidationCheck] = []

    neg_patterns = [
        r"\b(must not|shall not)\s+\w+",
        r"\b(never|do not|don't)\s+\w+",
        r"\b(prohibited|forbidden|avoid)\s+\w+",
        r"\bno\s+\w+\s+(?:allowed|permitted)",
    ]

    original_lower = original.lower()
    optimized_lower = optimized.lower()

    for pattern in neg_patterns:
        for match in re.finditer(pattern, original_lower, re.IGNORECASE):
            matched_text = match.group(0)
            req = Requirement(
                text=matched_text,
                type="negative",
                is_critical=True,
            )

            # Check if negation preserved
            if matched_text.lower() in optimized_lower:
                checks.append(
                    ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.EXACT,
                        evidence=matched_text,
                        confidence=1.0,
                    )
                )
            else:
                # Check if key verb preserved but negation dropped
                pattern = r"(?:not|never|don't|avoid|prohibited|forbidden)\s+(\w+)"
                verb_match = re.search(pattern, matched_text)
                if verb_match:
                    verb = verb_match.group(1)
                    if verb in optimized_lower:
                        checks.append(
                            ValidationCheck(
                                requirement=req,
                                status=PreservationStatus.WEAKENED,
                                evidence=f"Verb '{verb}' present but negation missing",
                                confidence=0.85,
                                notes="Negative constraint may have been weakened",
                            )
                        )
                    else:
                        checks.append(
                            ValidationCheck(
                                requirement=req,
                                status=PreservationStatus.MISSING,
                                evidence=f"Negative constraint completely missing: {matched_text}",
                                confidence=0.9,
                            )
                        )

    return checks


def _compare_lines(original: str, optimized: str) -> list[ValidationCheck]:
    """Line-by-line comparison using difflib."""
    checks: list[ValidationCheck] = []

    orig_lines = original.splitlines()
    opt_lines = optimized.splitlines()

    matcher = difflib.SequenceMatcher(None, orig_lines, opt_lines)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for idx in range(i1, i2):
                req = Requirement(
                    text=orig_lines[idx],
                    type="value",
                )
                checks.append(
                    ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.EXACT,
                        evidence=orig_lines[idx],
                        confidence=1.0,
                    )
                )
        elif tag == "delete":
            for idx in range(i1, i2):
                req = Requirement(
                    text=orig_lines[idx],
                    type="value",
                )
                checks.append(
                    ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MISSING,
                        evidence=orig_lines[idx],
                        confidence=0.9,
                    )
                )
        elif tag == "insert":
            # New lines in optimized - not a problem per se
            pass
        elif tag == "replace":
            for idx in range(i1, i2):
                req = Requirement(
                    text=orig_lines[idx],
                    type="value",
                )
                checks.append(
                    ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MODIFIED,
                        evidence=orig_lines[idx],
                        optimized_text="\n".join(opt_lines[j1:j2]) if j1 < j2 else "",
                        confidence=0.6,
                    )
                )

    return checks


def _extract_key_terms(text: str) -> list[str]:
    """Extract key terms from requirement text."""
    # Remove common stop words and extract meaningful terms
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "should", "could", "may", "might", "must", "shall", "can",
        "need", "want", "like", "please", "ensure", "make", "provide", "give",
    }

    words = re.findall(r"\b\w+\b", text.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]