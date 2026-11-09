"""Markdown report exporter for TokenSentry."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from tokensentry.models import (
    AnalysisReport,
    OptimizationResult,
    ValidationReport,
    Finding,
    Severity,
    OptimizationProfile,
    PromptSection,
    Requirement,
    TechnicalLiteral,
    ValidationCheck,
    PreservationStatus,
)


class MarkdownExporter:
    """Export reports as human-readable Markdown."""

    def export_analysis(self, report: AnalysisReport) -> str:
        """Export analysis report as Markdown."""
        lines = [
            f"# TokenSentry Analysis Report",
            f"**Prompt ID:** {report.prompt_id}",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Tokenizer:** {report.tokenizer.name} ({report.tokenizer.count_kind.value})",
            f"**Exact Count:** {'Yes' if report.tokenizer.is_exact else 'No'}",
            "",
            "## Statistics",
            f"- Characters: {report.stats.characters:,}",
            f"- Words: {report.stats.words:,}",
            f"- Lines: {report.stats.lines:,}",
            f"- Non-empty Lines: {report.stats.non_empty_lines:,}",
            f"- Avg Line Length: {report.stats.avg_line_length:.1f}",
            f"- Max Line Length: {report.stats.max_line_length:,}",
            f"- Token Count: {report.token_count:,} ({report.tokenizer.count_kind.value})",
            "",
        ]

        if report.quality_scores:
            lines.append("## Quality Scores")
            for name, score in report.quality_scores.items():
                lines.append(f"- **{name.capitalize()}:** {score:.2f}")
            lines.append("")

        if report.sections:
            lines.append("## Sections")
            for section in report.sections:
                lines.append(f"- **{section.type}** (lines {section.start_line}-{section.end_line})"
                             f"{f': {section.title}' if section.title else ''}"
                             f"{f' [{section.language}]' if section.language else ''}")
            lines.append("")

        if report.requirements:
            lines.append("## Requirements")
            by_type = {}
            for req in report.requirements:
                by_type.setdefault(req.type, []).append(req)
            for req_type, reqs in by_type.items():
                lines.append(f"### {req_type.capitalize()}")
                for req in reqs:
                    lines.append(f"- {req.text}")
                    if req.exact_value:
                        lines.append(f"  - *Value:* {req.exact_value}")
                lines.append("")

        if report.technical_literals:
            lines.append("## Technical Literals")
            by_type = {}
            for lit in report.technical_literals:
                by_type.setdefault(lit.type, []).append(lit)
            for lit_type, literals in by_type.items():
                lines.append(f"### {lit_type.capitalize()}")
                for lit in literals:
                    lines.append(f"- `{lit.value}` (priority: {lit.preservation_priority})")
                lines.append("")

        if report.findings:
            lines.append("## Findings")
            for finding in report.findings:
                severity_emoji = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨",
                }.get(finding.severity.value, "•")
                lines.append(f"### {severity_emoji} {finding.severity.value.upper()}: {finding.code}")
                lines.append(f"{finding.message}")
                if finding.evidence:
                    lines.append(f"**Evidence:** {finding.evidence}")
                if finding.suggestion:
                    lines.append(f"**Suggestion:** {finding.suggestion}")
                lines.append("")

        return "\n".join(lines)

    def export_optimization(self, result: OptimizationResult) -> str:
        """Export optimization result as Markdown."""
        lines = [
            f"# TokenSentry Optimization Report",
            f"**Profile:** {result.profile.value}",
            f"**Tokenizer:** {result.tokenizer.name}",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Token Count",
            f"- Original: {result.original_token_count:,}",
            f"- Optimized: {result.optimized_token_count:,}",
            f"- Delta: {result.token_delta:+,d} ({result.token_reduction_pct:+.1f}%)",
            "",
        ]

        if result.transformations:
            lines.append("## Transformations")
            for i, t in enumerate(result.transformations, 1):
                risk_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(t.risk_level.value, "•")
                lines.append(f"### {i}. {risk_emoji} {t.type}")
                lines.append(f"{t.description}")
                lines.append(f"**Risk:** {t.risk_level.value}")
                if t.token_delta:
                    lines.append(f"**Token Delta:** {t.token_delta:+,d}")
                if t.preserved_literals:
                    lines.append(f"**Preserved Literals:** {', '.join(t.preserved_literals)}")
                lines.append("")

        if result.warnings:
            lines.append("## Warnings")
            for w in result.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

        if result.preserved_literals:
            lines.append("## Preserved Literals")
            for lit in result.preserved_literals:
                lines.append(f"- `{lit.value}` ({lit.type}, priority: {lit.preservation_priority})")
            lines.append("")

        return "\n".join(lines)

    def export_validation(self, report: ValidationReport) -> str:
        """Export validation report as Markdown."""
        status = "✅ PASS" if report.passed else "❌ REVIEW REQUIRED"
        lines = [
            f"# TokenSentry Validation Report",
            f"**Status:** {status}",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- **Preserved:** {len(report.preserved_lines)}",
            f"- **Missing:** {len(report.missing_lines)}",
            f"- **Modified:** {len(report.modified_lines)}",
            f"- **Weakened Negatives:** {len(report.weakened_negatives)}",
            "",
        ]

        if report.summary:
            lines.append("## Detailed Counts")
            for key, value in report.summary.items():
                lines.append(f"- {key.capitalize()}: {value}")
            lines.append("")

        if report.missing_lines:
            lines.append("## ❌ Missing Requirements")
            for line in report.missing_lines:
                lines.append(f"- {line}")
            lines.append("")

        if report.modified_lines:
            lines.append("## ⚠️ Modified Requirements")
            for line in report.modified_lines:
                lines.append(f"- {line}")
            lines.append("")

        if report.weakened_negatives:
            lines.append("## 🔻 Weakened Negative Constraints")
            for line in report.weakened_negatives:
                lines.append(f"- {line}")
            lines.append("")

        if report.checks:
            lines.append("## Detailed Checks")
            for check in report.checks:
                status_emoji = {
                    "exact": "✅",
                    "structural": "✅",
                    "probable": "🟡",
                    "uncertain": "🟠",
                    "missing": "❌",
                    "modified": "⚠️",
                    "weakened": "🔻",
                }.get(check.status.value, "•")
                lines.append(f"### {status_emoji} {check.status.value.upper()}")
                lines.append(f"**Requirement:** {check.requirement.text}")
                lines.append(f"**Type:** {check.requirement.type}")
                if check.evidence:
                    lines.append(f"**Evidence:** {check.evidence}")
                if check.optimized_text:
                    lines.append(f"**In Optimized:** {check.optimized_text}")
                lines.append(f"**Confidence:** {check.confidence:.0%}")
                if check.notes:
                    lines.append(f"**Notes:** {check.notes}")
                lines.append("")

        if report.warnings:
            lines.append("## Warnings")
            for w in report.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

        return "\n".join(lines)

    def export_combined(
        self,
        analysis: Any = None,
        optimization: Any = None,
        validation: Any = None,
    ) -> str:
        """Export combined report as Markdown."""
        lines = [
            "# TokenSentry Combined Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
        ]

        if analysis:
            lines.append(self.export_analysis(analysis))
            lines.append("---")
            lines.append("")

        if optimization:
            lines.append(self.export_optimization(optimization))
            lines.append("---")
            lines.append("")

        if validation:
            lines.append(self.export_validation(validation))

        return "\n".join(lines)


def export_analysis_markdown(report: Any) -> str:
    """Convenience function to export analysis as Markdown."""
    return MarkdownExporter().export_analysis(report)


def export_optimization_markdown(result: Any) -> str:
    """Convenience function to export optimization as Markdown."""
    return MarkdownExporter().export_optimization(result)


def export_validation_markdown(report: Any) -> str:
    """Convenience function to export validation as Markdown."""
    return MarkdownExporter().export_validation(report)


def export_combined_markdown(
    analysis: Any = None,
    optimization: Any = None,
    validation: Any = None,
) -> str:
    """Convenience function to export combined report as Markdown."""
    return MarkdownExporter().export_combined(analysis, optimization, validation)