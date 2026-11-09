"""Prompt structure analysis - section parsing and hierarchy."""

from __future__ import annotations

import re
from typing import Any

from tokensentry.analysis import BaseAnalyzer
from tokensentry.models import PromptSection


class StructureAnalyzer(BaseAnalyzer):
    """Analyze prompt structure - headings, code fences, lists, schemas."""

    name = "structure"
    description = "Parse prompt into logical sections with hierarchy"

    # Patterns
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
    CODE_FENCE_PATTERN = re.compile(r"^```(\w*)\s*$")
    LIST_PATTERN = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.+)$")
    TABLE_PATTERN = re.compile(r"^\|.*\|$")
    HORIZONTAL_RULE = re.compile(r"^[-*_]{3,}\s*$")

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Any],
        technical_literals: list[Any],
    ) -> list[Any]:
        """Analyze prompt structure."""
        findings: list[Any] = []

        if not sections:
            findings.append(self._make_finding(
                "NO_SECTIONS",
                "info",
                "No sections detected in prompt",
                "Consider adding structure with headings or sections",
            ))
            return findings

        # Check for heading hierarchy
        headings = [s for s in sections if s.type == "heading"]
        if headings:
            findings.extend(self._check_heading_hierarchy(headings))

        # Check for code fences without language
        code_fences = [s for s in sections if s.type == "code_fence"]
        for fence in code_fences:
            if not fence.language:
                findings.append(self._make_finding(
                    "CODE_FENCE_NO_LANGUAGE",
                    "info",
                    f"Code fence at line {fence.start_line} has no language specified",
                    "Add language hint for syntax highlighting (e.g., ```python)",
                    (fence.start_line, fence.end_line),
                ))

        # Check for tables
        tables = [s for s in sections if s.type == "table"]
        if tables:
            findings.append(self._make_finding(
                "TABLES_DETECTED",
                "info",
                f"Found {len(tables)} table(s) in prompt",
                "Tables are token-intensive; consider if all are necessary",
            ))

        # Check section balance
        findings.extend(self._check_section_balance(sections))

        return findings

    def _check_heading_hierarchy(self, headings: list[PromptSection]) -> list[Any]:
        """Check heading level hierarchy."""
        findings: list[Any] = []
        prev_level = 0

        for h in headings:
            level = h.level or 1
            if prev_level > 0 and level > prev_level + 1:
                findings.append(self._make_finding(
                    "HEADING_LEVEL_SKIP",
                    "warning",
                    f"Heading level jumps from H{prev_level} to H{level}",
                    "Use sequential heading levels for better structure",
                    (h.start_line, h.end_line),
                ))
            prev_level = level

        return findings

    def _check_section_balance(self, sections: list[PromptSection]) -> list[Any]:
        """Check if sections are reasonably balanced."""
        findings: list[Any] = []

        # Count section types
        type_counts: dict[str, int] = {}
        for s in sections:
            type_counts[s.type] = type_counts.get(s.type, 0) + 1

        # Warn if too many paragraphs without structure
        para_count = type_counts.get("paragraph", 0)
        if para_count > 10 and type_counts.get("heading", 0) == 0:
            findings.append(self._make_finding(
                "MANY_PARAGRAPHS_NO_HEADINGS",
                "info",
                f"Found {para_count} paragraphs but no headings",
                "Consider adding headings to organize content",
            ))

        # Warn if very long single section
        for s in sections:
            content_lines = s.content.count("\n")
            if content_lines > 50 and s.type == "paragraph":
                findings.append(self._make_finding(
                    "VERY_LONG_PARAGRAPH",
                    "info",
                    f"Paragraph section at lines {s.start_line}-{s.end_line} has {content_lines} lines",
                    "Consider breaking into smaller sections",
                    (s.start_line, s.end_line),
                ))

        return findings

    def _make_finding(self, code: str, severity: str, message: str, suggestion: str, location: tuple[int, int] | None = None) -> Any:
        from tokensentry.models import Finding, Severity
        return Finding(
            code=code,
            severity=Severity(severity),
            message=message,
            suggestion=suggestion,
            location=location,
        )


# Standalone function for parsing (used by main analyzer)
def parse_sections(prompt: str) -> list[PromptSection]:
    """Parse prompt into logical sections."""
    StructureAnalyzer()
    # This is a simplified version - the full logic is in the old analyzer
    # For now, return empty list as placeholder
    return []


# Register analyzer
from tokensentry.analysis import registry

registry.register(StructureAnalyzer())