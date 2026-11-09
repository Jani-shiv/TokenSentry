"""Terminal report exporter for TokenSentry using Rich."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tokensentry.models import (
    AnalysisReport,
    Finding,
    OptimizationProfile,
    OptimizationResult,
    ValidationReport,
    PreservationStatus,
    Severity,
    ValidationCheck,
    TechnicalLiteral,
    PromptSection,
    Requirement,
)


class TerminalExporter:
    """Export reports as Rich terminal output."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def export_analysis(self, report: AnalysisReport) -> None:
        """Export analysis report to terminal."""
        exact_str = "Yes" if report.tokenizer.is_exact else "No"
        self.console.print(Panel.fit(
            f"[bold]Prompt ID:[/bold] {report.prompt_id}\n"
            f"[bold]Tokenizer:[/bold] {report.tokenizer.name} ({report.tokenizer.count_kind.value})\n"
            f"[bold]Exact Count:[/bold] {report.tokenizer.is_exact}\n"
            f"[bold]Characters:[/bold] {report.stats.characters:,}\n"
            f"[bold]Words:[/bold] {report.stats.words:,}\n"
            f"[bold]Lines:[/bold] {report.stats.lines:,}\n"
            f"[bold]Token Count:[/bold] {report.token_count:,} ({report.tokenizer.count_kind.value})",
            title="TokenSentry Analysis",
            border_style="cyan",
        ))

        if report.quality_scores:
            table = Table(title="Quality Scores", show_header=True, header_style="bold magenta")
            table.add_column("Dimension", style="white")
            table.add_column("Score", style="green")
            for name, score in report.quality_scores.items():
                table.add_row(name.capitalize(), f"{score:.2f}")
            self.console.print(table)

        if report.sections:
            table = Table(title="Sections", show_header=True, header_style="bold blue")
            table.add_column("Type", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Lines", style="yellow")
            table.add_column("Language", style="green")
            for s in report.sections:
                table.add_row(s.type, s.title or "-", f"{s.start_line}-{s.end_line}", s.language or "-")
            self.console.print(table)

        if report.requirements:
            table = Table(title="Requirements", show_header=True, header_style="bold yellow")
            table.add_column("Type", style="cyan")
            table.add_column("Text", style="white")
            table.add_column("Critical", style="red")
            table.add_column("Value", style="green")
            for req in report.requirements:
                table.add_row(req.type, req.text[:80] + "..." if len(req.text) > 80 else req.text,
                              "Yes" if req.is_critical else "No", req.exact_value or "-")
            self.console.print(table)

        if report.technical_literals:
            table = Table(title="Technical Literals", show_header=True, header_style="bold green")
            table.add_column("Type", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Priority", style="red")
            for lit in report.technical_literals:
                table.add_row(lit.type, lit.value[:60] + "..." if len(lit.value) > 60 else lit.value, str(lit.preservation_priority))
            self.console.print(table)

        if report.findings:
            self.console.print("\n[bold]Findings:[/bold]")
            for finding in report.findings:
                severity_style = {"info": "blue", "warning": "yellow", "error": "red", "critical": "bold red"}.get(finding.severity.value, "white")
                self.console.print(f"  [{severity_style}]{finding.severity.value.upper()}[/{severity_style}] [bold]{finding.code}[/bold]: {finding.message}")
                if finding.evidence:
                    self.console.print(f"    Evidence: {finding.evidence}")
                if finding.suggestion:
                    self.console.print(f"    Suggestion: {finding.suggestion}")

    def export_optimization(self, result: OptimizationResult) -> None:
        delta_color = "green" if result.token_delta >= 0 else "red"
        self.console.print(Panel.fit(
            f"[bold]Profile:[/bold] {result.profile.value}\n"
            f"[bold]Tokenizer:[/bold] {result.tokenizer.name}\n"
            f"[bold]Original Tokens:[/bold] {result.original_token_count:,}\n"
            f"[bold]Optimized Tokens:[/bold] {result.optimized_token_count:,}\n"
            f"[bold]Token Delta:[/bold] [{delta_color}]{result.token_delta:+,d} ({result.token_reduction_pct:+.1f}%)[/{delta_color}]\n"
            f"[bold]Transformations:[/bold] {len(result.transformations)}",
            title="TokenSentry Optimization",
            border_style="green" if result.token_delta >= 0 else "yellow",
        ))

        if result.transformations:
            table = Table(title="Transformations", show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim")
            table.add_column("Type", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Risk", style="red")
            table.add_column("Token Delta", style="yellow")
            for i, t in enumerate(result.transformations, 1):
                risk_emoji = {"info": "i", "warning": "!", "error": "x"}.get(t.risk_level.value, "?")
                table.add_row(str(i), t.type, t.description, f"{risk_emoji} {t.risk_level.value}", f"{t.token_delta:+,d}" if t.token_delta else "0")
            self.console.print(table)

        if result.warnings:
            self.console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for w in result.warnings:
                self.console.print(f"  Warning: {w}")

        if result.preserved_literals:
            table = Table(title="Preserved Literals", show_header=True, header_style="bold green")
            table.add_column("Type", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Priority", style="red")
            for lit in result.preserved_literals:
                table.add_row(lit.type, lit.value[:60] + "..." if len(lit.value) > 60 else lit.value, str(lit.preservation_priority))
            self.console.print(table)

    def export_validation(self, report: ValidationReport) -> None:
        status_color = "green" if report.passed else "red"
        status_text = "PASS" if report.passed else "REVIEW REQUIRED"

        self.console.print(Panel.fit(
            f"[{status_color}]{status_text}[/{status_color}]\n"
            f"[bold]Preserved:[/bold] {len(report.preserved_lines)}\n"
            f"[bold]Missing:[/bold] {len(report.missing_lines)}\n"
            f"[bold]Modified:[/bold] {len(report.modified_lines)}\n"
            f"[bold]Weakened:[/bold] {len(report.weakened_negatives)}",
            title="TokenSentry Validation",
            border_style="green" if report.passed else "red",
        ))

        if report.summary:
            table = Table(title="Summary", show_header=True, header_style="bold magenta")
            table.add_column("Status", style="cyan")
            table.add_column("Count", style="yellow")
            for key, value in report.summary.items():
                table.add_row(key.capitalize(), str(value))
            self.console.print(table)

        if report.missing_lines:
            self.console.print("\n[bold red]Missing Requirements:[/bold red]")
            for line in report.missing_lines[:10]:
                self.console.print(f"  - {line[:120]}")
            if len(report.missing_lines) > 10:
                self.console.print(f"  ... and {len(report.missing_lines) - 10} more")

        if report.modified_lines:
            self.console.print("\n[bold yellow]Modified Requirements:[/bold yellow]")
            for line in report.modified_lines[:10]:
                self.console.print(f"  - {line[:120]}")

        if report.weakened_negatives:
            self.console.print("\n[bold red]Weakened Negative Constraints:[/bold red]")
            for line in report.weakened_negatives[:10]:
                self.console.print(f"  - {line[:120]}")

        if report.checks:
            table = Table(title="Detailed Checks", show_header=True, header_style="bold cyan")
            table.add_column("Status", style="white")
            table.add_column("Requirement", style="white")
            table.add_column("Type", style="cyan")
            table.add_column("Confidence", style="green")
            for check in report.checks[:20]:
                status_emoji = {"exact": "OK", "structural": "OK", "probable": "~", "uncertain": "?", "missing": "X", "modified": "M", "weakened": "W"}.get(check.status.value, "?")
                req_text = check.requirement.text[:80] + "..." if len(check.requirement.text) > 80 else check.requirement.text
                table.add_row(f"{status_emoji} {check.status.value}", req_text, check.requirement.type, f"{check.confidence:.0%}")
            self.console.print(table)

        if report.warnings:
            self.console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for w in report.warnings:
                self.console.print(f"  Warning: {w}")


def print_analysis(report):
    TerminalExporter().export_analysis(report)


def print_optimization(result):
    TerminalExporter().export_optimization(result)


def print_validation(report):
    TerminalExporter().export_validation(report)