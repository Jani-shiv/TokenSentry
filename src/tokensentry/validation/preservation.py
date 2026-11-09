"""Enhanced preservation checking for validation."""

from __future__ import annotations

import difflib
import re
from typing import Any

from tokensentry.models import (
    PreservationStatus,
    Requirement,
    TechnicalLiteral,
    ValidationCheck,
)
from tokensentry.validation.schemas import (
    SchemaValidationError,
    compare_structures,
    detect_output_format,
)


class PreservationValidator:
    """Enhanced validator for requirement and literal preservation."""

    def __init__(self) -> None:
        self.checks: list[ValidationCheck] = []

    def validate(
        self,
        original: str,
        optimized: str,
        original_requirements: list[Requirement] | None = None,
        original_literals: list[TechnicalLiteral] | None = None,
    ) -> list[ValidationCheck]:
        """Run all preservation checks."""
        self.checks = []

        # Extract requirements if not provided
        if original_requirements is None:
            original_requirements = self._extract_requirements(original)

        if original_literals is None:
            original_literals = self._find_technical_literals(original)

        # 1. Requirement preservation
        self._check_requirements(original_requirements, optimized)

        # 2. Technical literal preservation (byte-for-byte for code/commands)
        self._check_literals(original_literals, optimized)

        # 3. Negative constraint weakening
        self._check_negative_constraints(original, optimized, original_requirements)

        # 4. Output schema preservation
        self._check_output_schema(original, optimized)

        # 5. Line-by-line structural comparison
        self._compare_structure(original, optimized)

        return self.checks

    def _extract_requirements(self, text: str) -> list[Requirement]:
        """Extract requirements from text."""
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
                for match in re.finditer(pattern, line_lower, re.IGNORECASE):
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

    def _find_technical_literals(self, text: str) -> list[TechnicalLiteral]:
        """Find technical literals that must be preserved."""
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

    def _check_requirements(
        self, requirements: list[Requirement], optimized: str
    ) -> None:
        """Check if requirements are preserved in optimized text."""
        optimized_lower = optimized.lower()

        for req in requirements:
            req_text = req.text.strip()
            req_lower = req_text.lower()

            # Exact match
            if req_text in optimized:
                self.checks.append(ValidationCheck(
                    requirement=req,
                    status=PreservationStatus.EXACT,
                    evidence=req_text,
                    optimized_text=req_text,
                    confidence=1.0,
                ))
                continue

            # Key terms extraction
            key_terms = self._extract_key_terms(req_text)
            if key_terms:
                matches = sum(1 for term in key_terms if term.lower() in optimized_lower)
                ratio = matches / len(key_terms)

                if ratio >= 0.9:
                    status = PreservationStatus.STRUCTURAL
                    confidence = 0.9
                elif ratio >= 0.7:
                    status = PreservationStatus.PROBABLE
                    confidence = 0.7
                elif ratio >= 0.5:
                    status = PreservationStatus.UNCERTAIN
                    confidence = 0.5
                else:
                    status = PreservationStatus.MISSING
                    confidence = 0.9

                self.checks.append(ValidationCheck(
                    requirement=req,
                    status=status,
                    evidence=f"Key terms preserved: {matches}/{len(key_terms)}",
                    confidence=confidence,
                ))

                if status == PreservationStatus.MISSING:
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MISSING,
                        evidence="Requirement not found in optimized prompt",
                        confidence=0.9,
                    ))
            else:
                # No key terms extracted
                if req.type == "negative":
                    neg_terms = ["not", "never", "no", "don't", "must not", "shall not", "prohibited", "forbidden"]
                    has_negation = any(term in req_lower for term in neg_terms)
                    opt_has_negation = any(term in optimized_lower for term in neg_terms)

                    if has_negation and not opt_has_negation:
                        self.checks.append(ValidationCheck(
                            requirement=req,
                            status=PreservationStatus.WEAKENED,
                            evidence="Negative constraint appears to be weakened or removed",
                            confidence=0.8,
                            notes="Negative instruction may have been dropped during optimization",
                        ))
                    else:
                        self.checks.append(ValidationCheck(
                            requirement=req,
                            status=PreservationStatus.MISSING,
                            evidence="Negative requirement not found in optimized prompt",
                            confidence=0.9,
                        ))
                else:
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MISSING,
                        evidence="Requirement not found in optimized prompt",
                        confidence=0.9,
                    ))

    def _check_literals(
        self, literals: list[TechnicalLiteral], optimized: str
    ) -> None:
        """Check if technical literals are preserved byte-for-byte."""
        for lit in literals:
            # Create a requirement-like object for the literal
            req = Requirement(
                text=f"[{lit.type}] {lit.value}",
                type="value",
                is_critical=lit.preservation_priority >= 8,
            )

            if lit.value in optimized:
                self.checks.append(ValidationCheck(
                    requirement=req,
                    status=PreservationStatus.EXACT,
                    evidence=lit.value,
                    optimized_text=lit.value,
                    confidence=1.0,
                ))
                continue

            # For code/commands, check fuzzy match
            if lit.type in ("code", "command", "json", "yaml"):
                matcher = difflib.SequenceMatcher(None, lit.value, optimized)
                match = matcher.find_longest_match(0, len(lit.value), 0, len(optimized))
                if match.size >= len(lit.value) * 0.8:
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.STRUCTURAL,
                        evidence=f"Similar content found ({match.size}/{len(lit.value)} chars)",
                        confidence=0.8,
                    ))
                else:
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MISSING,
                        evidence=f"Literal not found: {lit.value[:100]}",
                        confidence=0.9,
                    ))
            else:
                self.checks.append(ValidationCheck(
                    requirement=req,
                    status=PreservationStatus.MISSING,
                    evidence=f"Literal not found: {lit.value[:100]}",
                    confidence=0.9,
                ))

    def _check_negative_constraints(
        self, original: str, optimized: str, requirements: list[Requirement]
    ) -> None:
        """Specifically check negative constraint preservation."""
        original_lower = original.lower()
        optimized_lower = optimized.lower()

        neg_patterns = [
            r"\b(must not|shall not)\s+\w+",
            r"\b(never|do not|don't)\s+\w+",
            r"\b(prohibited|forbidden|avoid)\s+\w+",
            r"\bno\s+\w+\s+(?:allowed|permitted)",
        ]

        for pattern in neg_patterns:
            for match in re.finditer(pattern, original_lower, re.IGNORECASE):
                matched_text = match.group(0)
                req = Requirement(
                    text=matched_text,
                    type="negative",
                    is_critical=True,
                )

                if matched_text.lower() in optimized_lower:
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.EXACT,
                        evidence=matched_text,
                        confidence=1.0,
                    ))
                else:
                    # Check if key verb preserved but negation dropped
                    verb_match = re.search(
                        r"(?:not|never|don't|avoid|prohibited|forbidden)\s+(\w+)",
                        matched_text
                    )
                    if verb_match:
                        verb = verb_match.group(1)
                        if verb in optimized_lower:
                            self.checks.append(ValidationCheck(
                                requirement=req,
                                status=PreservationStatus.WEAKENED,
                                evidence=f"Verb '{verb}' present but negation missing",
                                confidence=0.85,
                                notes="Negative constraint may have been weakened",
                            ))
                        else:
                            self.checks.append(ValidationCheck(
                                requirement=req,
                                status=PreservationStatus.MISSING,
                                evidence=f"Negative constraint completely missing: {matched_text}",
                                confidence=0.9,
                            ))

    def _check_output_schema(self, original: str, optimized: str) -> None:
        """Check output schema/structure preservation."""
        schema_errors = compare_structures(original, optimized)

        for error in schema_errors:
            req = Requirement(
                text=f"Output structure: {error}",
                type="schema",
                is_critical=True,
            )
            self.checks.append(ValidationCheck(
                requirement=req,
                status=PreservationStatus.MISSING,
                evidence=str(error),
                confidence=0.8,
            ))

    def _compare_structure(self, original: str, optimized: str) -> None:
        """Line-by-line structural comparison."""
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
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.EXACT,
                        evidence=orig_lines[idx],
                        confidence=1.0,
                    ))
            elif tag == "delete":
                for idx in range(i1, i2):
                    req = Requirement(
                        text=orig_lines[idx],
                        type="value",
                    )
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MISSING,
                        evidence=orig_lines[idx],
                        confidence=0.9,
                    ))
            elif tag == "replace":
                for idx in range(i1, i2):
                    req = Requirement(
                        text=orig_lines[idx],
                        type="value",
                    )
                    self.checks.append(ValidationCheck(
                        requirement=req,
                        status=PreservationStatus.MODIFIED,
                        evidence=orig_lines[idx],
                        optimized_text="\n".join(opt_lines[j1:j2]) if j1 < j2 else "",
                        confidence=0.6,
                    ))

    def _extract_key_terms(self, text: str) -> list[str]:
        """Extract key terms from requirement text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "must", "shall", "can",
            "need", "want", "like", "please", "ensure", "make", "provide", "give",
        }

        words = re.findall(r"\b\w+\b", text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]


def validate_prompt_enhanced(
    original: str,
    optimized: str,
    original_requirements: list[Requirement] | None = None,
    original_literals: list[TechnicalLiteral] | None = None,
) -> list[ValidationCheck]:
    """Enhanced validation with all preservation checks."""
    validator = PreservationValidator()
    return validator.validate(original, optimized, original_requirements, original_literals)