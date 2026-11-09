"""Complexity analysis - metrics for prompt complexity."""

from __future__ import annotations

import re

from tokensentry.analysis.registry import BaseAnalyzer, registry
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class ComplexityAnalyzer(BaseAnalyzer):
    """Compute complexity metrics for prompts."""

    name = "complexity"
    description = "Calculate structural complexity, nesting depth, and token density metrics"

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze prompt complexity."""
        findings: list[Finding] = []

        metrics = self._compute_metrics(prompt, sections)

        # Report metrics as findings
        findings.append(Finding(
            code="COMPLEXITY_METRICS",
            severity=Severity.INFO,
            message="Prompt complexity metrics computed",
            evidence=(
                f"Nesting depth: {metrics['nesting_depth']}, "
                f"Section count: {metrics['section_count']}, "
                f"Avg section length: {metrics['avg_section_length']:.1f} lines, "
                f"Requirement density: {metrics['requirement_density']:.2f}/section, "
                f"Token density: {metrics['token_density']:.1f} chars/token (est)"
            ),
            suggestion="Use metrics to guide optimization decisions",
        ))

        # Check for high complexity indicators
        if metrics["nesting_depth"] > 4:
            findings.append(Finding(
                code="HIGH_NESTING_DEPTH",
                severity=Severity.WARNING,
                message=f"High heading nesting depth: {metrics['nesting_depth']}",
                evidence="Deeply nested headings may confuse models",
                suggestion="Flatten hierarchy to max 3-4 levels",
            ))

        if metrics["section_count"] > 20:
            findings.append(Finding(
                code="MANY_SECTIONS",
                severity=Severity.INFO,
                message=f"Large number of sections: {metrics['section_count']}",
                evidence="Many small sections may fragment context",
                suggestion="Consider consolidating related sections",
            ))

        if metrics["avg_section_length"] > 30:
            findings.append(Finding(
                code="LONG_SECTIONS",
                severity=Severity.INFO,
                message=(
                    f"Average section length is high: "
                    f"{metrics['avg_section_length']:.1f} lines"
                ),
                evidence="Long sections may exceed effective attention span",
                suggestion="Break long sections into focused subsections",
            ))

        if metrics["requirement_density"] > 3:
            findings.append(Finding(
                code="HIGH_REQUIREMENT_DENSITY",
                severity=Severity.INFO,
                message=(
                    f"High requirement density: "
                    f"{metrics['requirement_density']:.1f} per section"
                ),
                evidence="Many requirements packed together",
                suggestion="Consider prioritizing or grouping requirements",
            ))

        # Instruction complexity
        findings.extend(self._analyze_instruction_complexity(prompt, sections))

        return findings

    def _compute_metrics(
        self,
        prompt: str,
        sections: list[PromptSection],
    ) -> dict[str, float]:
        """Compute complexity metrics."""

        # Nesting depth from headings
        headings = [s for s in sections if s.type == "heading"]
        nesting_depth = max((h.level or 1) for h in headings) if headings else 0

        # Section metrics
        section_count = len(sections)
        para_sections = [s for s in sections if s.type == "paragraph"]
        avg_section_length = (
            sum(s.content.count("\n") for s in para_sections) / len(para_sections)
            if para_sections else 0
        )

        # Requirement density
        requirement_density = len(sections) / section_count if section_count > 0 else 0

        # Token density estimate (chars per estimated token)
        char_count = len(prompt)
        estimated_tokens = max(1, char_count // 4)
        token_density = char_count / estimated_tokens

        return {
            "nesting_depth": nesting_depth,
            "section_count": section_count,
            "avg_section_length": avg_section_length,
            "requirement_density": requirement_density,
            "token_density": token_density,
        }

    def _analyze_instruction_complexity(
        self,
        prompt: str,
        sections: list[PromptSection],
    ) -> list[Finding]:
        """Analyze complexity of individual instructions."""
        findings: list[Finding] = []

        # Count imperative sentences
        imperative_patterns = [
            r"^\s*(?:please\s+)?"
            r"(?:create|write|generate|analyze|explain|list|describe|compare|"
            r"implement|build|design|develop|write|produce|output|return|"
            r"provide|give|show|display|print|format|convert|transform|"
            r"extract|parse|validate|check|verify|ensure|make|set|configure|"
            r"define|specify|indicate|state|include|add|remove|delete|"
            r"update|modify|change)\b",
        ]

        imperative_count = 0
        for line in prompt.splitlines():
            for pattern in imperative_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    imperative_count += 1
                    break

        if imperative_count > 15:
            findings.append(Finding(
                code="MANY_IMPERATIVES",
                severity=Severity.INFO,
                message=f"High number of imperative instructions: {imperative_count}",
                evidence="Many distinct commands may fragment model attention",
                suggestion="Group related instructions or use numbered steps",
            ))

        # Check for compound instructions (multiple verbs in one sentence)
        compound_count = 0
        verbs_pattern = r"\b(create|write|generate|analyze|explain|list|describe|" \
            r"compare|implement|build|design|develop|produce|output|return|" \
            r"provide|give|show|display|format|convert|transform|extract|" \
            r"parse|validate|check|verify|ensure|make|set|configure|define|" \
            r"specify|indicate|state|include|add|remove|delete|update|modify|change)\b"
        for line in prompt.splitlines():
            verbs = re.findall(verbs_pattern, line, re.IGNORECASE)
            if len(verbs) > 2:
                compound_count += 1

        if compound_count > 3:
            findings.append(Finding(
                code="COMPOUND_INSTRUCTIONS",
                severity=Severity.INFO,
                message=f"Found {compound_count} sentences with multiple action verbs",
                evidence="Compound instructions may be harder to follow",
                suggestion="Split into separate, single-action instructions",
            ))

        return findings


# Register
registry.register(ComplexityAnalyzer())