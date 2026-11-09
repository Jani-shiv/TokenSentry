"""Contradiction analysis - conflicting requirements detection."""

from __future__ import annotations

import re

from tokensentry.analysis.registry import BaseAnalyzer, registry
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class ContradictionAnalyzer(BaseAnalyzer):
    """Detect contradictory requirements and instructions."""

    name = "contradictions"
    description = "Detect conflicting instructions, incompatible constraints, and logical contradictions"

    # Contradiction patterns
    NEGATION_TERMS = ["not", "never", "no", "don't", "must not", "shall not",
                      "prohibited", "forbidden", "avoid", "exclude"]
    POSITIVE_TERMS = ["must", "shall", "required to", "have to", "should", "ensure"]

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze for contradictions."""
        findings: list[Finding] = []

        # 1. Direct positive/negative requirement conflicts
        findings.extend(self._find_direct_conflicts(requirements))

        # 2. Value constraint contradictions
        findings.extend(self._find_value_conflicts(requirements))

        # 3. Format/output contradictions
        findings.extend(self._find_format_conflicts(requirements))

        # 4. Instruction vs constraint contradictions
        findings.extend(self._find_instruction_constraint_conflicts(prompt, requirements))

        # 5. Temporal/logical contradictions
        findings.extend(self._find_logical_contradictions(prompt))

        return findings

    def _find_direct_conflicts(self, requirements: list[Requirement]) -> list[Finding]:
        """Find direct positive/negative conflicts."""
        findings: list[Finding] = []

        positive_reqs = [r for r in requirements if r.type == "positive"]
        negative_reqs = [r for r in requirements if r.type == "negative"]

        for pos in positive_reqs:
            for neg in negative_reqs:
                # Check for overlapping key terms
                pos_words = set(self._normalize_words(pos.text))
                neg_words = set(self._normalize_words(neg.text))

                # Remove common stop words
                stop_words = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with", "by", "use", "using"}
                pos_key = pos_words - stop_words
                neg_key = neg_words - stop_words

                overlap = pos_key & neg_key
                if len(overlap) >= 2:
                    # Check if it's a true contradiction (same action, opposite polarity)
                    findings.append(Finding(
                        code="CONTRADICTORY_REQUIREMENTS",
                        severity=Severity.WARNING,
                        message="Potential contradiction between positive and negative requirements",
                        evidence=f"Positive: {pos.text[:100]} | Negative: {neg.text[:100]}",
                        suggestion="Review conflicting requirements - they may be mutually exclusive",
                        location=pos.line_range or neg.line_range,
                    ))

        return findings

    def _find_value_conflicts(self, requirements: list[Requirement]) -> list[Finding]:
        """Find conflicting numeric constraints."""
        findings: list[Finding] = []

        value_reqs = [r for r in requirements if r.type == "value" and r.exact_value]

        for i, req1 in enumerate(value_reqs):
            for req2 in value_reqs[i+1:]:
                if req1.exact_value and req2.exact_value:
                    try:
                        val1 = int(req1.exact_value)
                        val2 = int(req2.exact_value)

                        # Check for direct min/max conflicts
                        if self._is_min_max_conflict(req1.text, req2.text, val1, val2):
                            findings.append(Finding(
                                code="CONFLICTING_VALUE_CONSTRAINTS",
                                severity=Severity.ERROR,
                                message=f"Conflicting numeric constraints: {val1} vs {val2}",
                                evidence=f"Req 1: {req1.text} | Req 2: {req2.text}",
                                suggestion="Resolve conflicting limits",
                                location=req1.line_range or req2.line_range,
                            ))
                    except ValueError:
                        pass

        return findings

    def _is_min_max_conflict(self, text1: str, text2: str, val1: int, val2: int) -> bool:
        """Check if two value constraints contradict."""
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        min_indicators = ["minimum", "at least", "no less than", "min"]
        max_indicators = ["maximum", "at most", "no more than", "max", "exactly"]

        is_min1 = any(ind in text1_lower for ind in min_indicators)
        is_max1 = any(ind in text1_lower for ind in max_indicators)
        is_min2 = any(ind in text2_lower for ind in min_indicators)
        is_max2 = any(ind in text2_lower for ind in max_indicators)

        # Min > Max conflict
        if is_min1 and is_max2 and val1 > val2:
            return True
        if is_min2 and is_max1 and val2 > val1:
            return True

        # Exact value conflicts
        if "exactly" in text1_lower and "exactly" in text2_lower and val1 != val2:
            return True

        return False

    def _find_format_conflicts(self, requirements: list[Requirement]) -> list[Finding]:
        """Find conflicting format requirements."""
        findings: list[Finding] = []

        format_reqs = [r for r in requirements if r.type in ("format", "output", "schema")]

        formats = set()
        for req in format_reqs:
            text = req.text.lower()
            for fmt in ["json", "yaml", "xml", "csv", "markdown", "html", "text", "table"]:
                if fmt in text:
                    formats.add(fmt)

        if len(formats) > 1:
            findings.append(Finding(
                code="CONFLICTING_FORMATS",
                severity=Severity.WARNING,
                message=f"Multiple output formats specified: {', '.join(formats)}",
                evidence=f"Formats found: {formats}",
                suggestion="Specify a single primary output format, or clarify if multiple are acceptable",
            ))

        return findings

    def _find_instruction_constraint_conflicts(self, prompt: str,
                                               requirements: list[Requirement]) -> list[Finding]:
        """Find conflicts between instructions and constraints."""
        findings: list[Finding] = []

        # Example: "Write a detailed explanation" + "Keep it under 50 words"
        detail_indicators = ["detailed", "comprehensive", "thorough", "in-depth", "extensive"]
        brevity_indicators = ["brief", "concise", "short", "under", "maximum", "limit", "few"]

        has_detail = any(ind in prompt.lower() for ind in detail_indicators)
        has_brevity = any(ind in prompt.lower() for ind in brevity_indicators)

        if has_detail and has_brevity:
            # Check if they're actually in conflict
            findings.append(Finding(
                code="DETAIL_BREVITY_CONFLICT",
                severity=Severity.INFO,
                message="Prompt requests both detail and brevity",
                evidence="Contains both detail-seeking and length-limiting language",
                suggestion="Clarify priority: detailed within constraints, or brief overview",
            ))

        return findings

    def _find_logical_contradictions(self, prompt: str) -> list[Finding]:
        """Find logical contradictions in prompt text."""
        findings: list[Finding] = []

        # "Do X but don't do X" patterns
        contradiction_patterns = [
            (r"(?:do|perform|execute)\s+(\w+).{0,100}(?:not|never|don't)\s+\1",
             "action prohibition conflict"),
            (r"(?:include|add|provide)\s+(\w+).{0,100}(?:exclude|remove|omit)\s+\1",
             "include/exclude conflict"),
            (r"(?:must|shall)\s+(\w+).{0,100}(?:must not|shall not)\s+\1",
             "must/must not conflict"),
        ]

        for pattern, desc in contradiction_patterns:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code="LOGICAL_CONTRADICTION",
                    severity=Severity.WARNING,
                    message=f"Logical contradiction detected: {desc}",
                    evidence=match.group(0)[:200],
                    suggestion="Review the conflicting instructions",
                    location=(line_num, line_num),
                ))

        return findings

    def _normalize_words(self, text: str) -> list[str]:
        """Extract meaningful words from text."""
        stop = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with", "by",
                "use", "using", "you", "your", "must", "shall", "should", "not", "never",
                "no", "be", "is", "are"}
        words = re.findall(r"\b\w+\b", text.lower())
        return [w for w in words if w not in stop and len(w) > 2]


# Register
registry.register(ContradictionAnalyzer())