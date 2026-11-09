"""TokenSentry CLI."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.panel import Panel
from rich.table import Table

from tokensentry.config import validate_file_path
from tokensentry.core import analyze_prompt, optimize_prompt, validate_prompt
from tokensentry.models import (
    AnalysisReport,
    OptimizationProfile,
    OptimizationResult,
    ValidationReport,
)
from tokensentry.tokenizers import list_tokenizers

app = typer.Typer(
    help="Local-first prompt analysis, optimization, and validation.",
    rich_markup_mode="rich",
)

ANALYZE_FILE_ARG = typer.Argument(
    ..., exists=True, readable=True, help="Prompt file to analyze"
)
OPTIMIZE_FILE_ARG = typer.Argument(
    ..., exists=True, readable=True, help="Prompt file to optimize"
)
VALIDATE_ORIGINAL_ARG = typer.Argument(
    ..., exists=True, readable=True, help="Original prompt file"
)
VALIDATE_OPTIMIZED_ARG = typer.Argument(
    ..., exists=True, readable=True, help="Optimized prompt file"
)
OUTPUT_OPTION = typer.Option(
    Path("optimized-prompt.md"), "--output", "-o", help="Output file for optimized prompt"
)
TOKENIZER_OPTION = typer.Option(
    None, "--tokenizer", "-t", help="Tokenizer to use (default: character-estimate)"
)
PROFILE_OPTION = typer.Option(
    OptimizationProfile.CONSERVATIVE, "--profile", "-p", help="Optimization profile"
)
FORMAT_OPTION = typer.Option(
    "terminal", "--format", "-f", help="Output format: json, markdown, terminal"
)
LIST_TOKENIZERS_FLAG = typer.Option(
    False, "--list-tokenizers", help="List available tokenizers and exit"
)


def _read_file(path: Path) -> str:
    """Read file with validation."""
    validated = validate_file_path(path)
    return validated.read_text(encoding="utf-8")


def _write_file(path: Path, content: str) -> None:
    """Write file."""
    path.write_text(content, encoding="utf-8")


def _print_analysis_report(report: AnalysisReport, format_: str) -> None:
    """Print analysis report in specified format."""
    if format_ == "json":
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return

    if format_ == "markdown":
        _print_analysis_markdown(report)
        return

    # Terminal format (default)
    table = Table(title="TokenSentry Analysis", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", style="green")

    table.add_row("Prompt ID", report.prompt_id)
    table.add_row("Characters", str(report.stats.characters))
    table.add_row("Words", str(report.stats.words))
    table.add_row("Lines", str(report.stats.lines))
    table.add_row("Non-empty lines", str(report.stats.non_empty_lines))
    table.add_row("Avg line length", f"{report.stats.avg_line_length:.1f}")
    table.add_row("Max line length", str(report.stats.max_line_length))
    table.add_row("Tokenizer", report.tokenizer.name)
    table.add_row("Token count", f"{report.token_count} ({report.tokenizer.count_kind.value})")
    table.add_row("Exact count", "Yes" if report.tokenizer.is_exact else "No")

    print(table)

    if report.findings:
        print("\n[bold yellow]Findings:[/bold yellow]")
        for finding in report.findings:
            severity_color = {
                "info": "blue",
                "warning": "yellow",
                "error": "red",
                "critical": "bold red",
            }.get(finding.severity.value, "white")
            print(f"  [{severity_color}]{finding.severity.value.upper()}[/{severity_color}] "
                  f"[bold]{finding.code}[/bold]: {finding.message}")
            if finding.evidence:
                print(f"    Evidence: {finding.evidence}")
            if finding.suggestion:
                print(f"    Suggestion: {finding.suggestion}")

    if report.quality_scores:
        print("\n[bold cyan]Quality Scores:[/bold cyan]")
        for name, score in report.quality_scores.items():
            print(f"  {name}: {score:.2f}")

    if report.sections:
        print(f"\n[bold]Sections:[/bold] {len(report.sections)} parsed")
    if report.requirements:
        print(f"[bold]Requirements:[/bold] {len(report.requirements)} extracted")
    if report.technical_literals:
        print(f"[bold]Technical Literals:[/bold] {len(report.technical_literals)} identified")


def _print_analysis_markdown(report: AnalysisReport) -> None:
    """Print analysis report as Markdown."""
    lines = [
        "# TokenSentry Analysis Report",
        f"**Prompt ID:** {report.prompt_id}",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Statistics",
        f"- Characters: {report.stats.characters}",
        f"- Words: {report.stats.words}",
        f"- Lines: {report.stats.lines}",
        f"- Non-empty lines: {report.stats.non_empty_lines}",
        f"- Avg line length: {report.stats.avg_line_length:.1f}",
        f"- Max line length: {report.stats.max_line_length}",
        "",
        "## Tokenization",
        f"- Tokenizer: {report.tokenizer.name}",
        f"- Token count: {report.token_count} ({report.tokenizer.count_kind.value})",
        f"- Exact: {'Yes' if report.tokenizer.is_exact else 'No'}",
        "",
    ]

    if report.quality_scores:
        lines.append("## Quality Scores")
        for name, score in report.quality_scores.items():
            lines.append(f"- {name}: {score:.2f}")
        lines.append("")

    if report.findings:
        lines.append("## Findings")
        for finding in report.findings:
            lines.append(f"### {finding.severity.value.upper()}: {finding.code}")
            lines.append(f"{finding.message}")
            if finding.evidence:
                lines.append(f"**Evidence:** {finding.evidence}")
            if finding.suggestion:
                lines.append(f"**Suggestion:** {finding.suggestion}")
            lines.append("")

    print("\n".join(lines))


def _print_optimization_result(result: OptimizationResult, format_: str) -> None:
    """Print optimization result in specified format."""
    if format_ == "json":
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return

    if format_ == "markdown":
        _print_optimization_markdown(result)
        return

    # Terminal format
    print(Panel.fit(
        f"[bold]Profile:[/bold] {result.profile.value}\n"
        f"[bold]Tokenizer:[/bold] {result.tokenizer.name}\n"
        f"[bold]Original tokens:[/bold] {result.original_token_count}\n"
        f"[bold]Optimized tokens:[/bold] {result.optimized_token_count}\n"
        f"[bold]Token delta:[/bold] {result.token_delta:+d} ({result.token_reduction_pct:+.1f}%)\n"
        f"[bold]Transformations:[/bold] {len(result.transformations)}",
        title="TokenSentry Optimization",
    ))

    if result.transformations:
        print("\n[bold]Transformations:[/bold]")
        risk_map = {"info": "blue", "warning": "yellow", "error": "red"}
        for i, t in enumerate(result.transformations, 1):
            risk_color = risk_map.get(t.risk_level.value, "white")
            print(f"  {i}. [{risk_color}]{t.type}[/{risk_color}]: {t.description}")

    if result.warnings:
        print("\n[bold yellow]Warnings:[/bold yellow]")
        for w in result.warnings:
            print(f"  - {w}")

    if result.preserved_literals:
        print(f"\n[bold]Preserved literals:[/bold] {len(result.preserved_literals)}")


def _print_optimization_markdown(result: OptimizationResult) -> None:
    """Print optimization result as Markdown."""
    lines = [
        "# TokenSentry Optimization Report",
        f"**Profile:** {result.profile.value}",
        f"**Tokenizer:** {result.tokenizer.name}",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Token Count",
        f"- Original: {result.original_token_count}",
        f"- Optimized: {result.optimized_token_count}",
        f"- Delta: {result.token_delta:+d} ({result.token_reduction_pct:+.1f}%)",
        "",
    ]

    if result.transformations:
        lines.append("## Transformations")
        for i, t in enumerate(result.transformations, 1):
            lines.append(f"### {i}. {t.type}")
            lines.append(f"{t.description}")
            orig = t.original[:100] + "..." if len(t.original) > 100 else t.original
            opt = t.optimized[:100] + "..." if len(t.optimized) > 100 else t.optimized
            lines.append(f"- Original: `{orig}`")
            lines.append(f"- Optimized: `{opt}`")
            lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    print("\n".join(lines))


def _print_validation_report(report: ValidationReport, format_: str) -> None:
    """Print validation report in specified format."""
    if format_ == "json":
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return

    if format_ == "markdown":
        _print_validation_markdown(report)
        return

    # Terminal format
    status = "[green]PASS[/green]" if report.passed else "[red]REVIEW REQUIRED[/red]"
    print(Panel.fit(
        f"{status}\n"
        f"Preserved: {len(report.preserved_lines)} | "
        f"Missing: {len(report.missing_lines)} | "
        f"Modified: {len(report.modified_lines)} | "
        f"Weakened: {len(report.weakened_negatives)}",
        title="TokenSentry Validation",
    ))

    if report.missing_lines:
        print("\n[bold red]Missing:[/bold red]")
        for line in report.missing_lines[:10]:
            print(f"  - {line[:200]}")
        if len(report.missing_lines) > 10:
            print(f"  ... and {len(report.missing_lines) - 10} more")

    if report.modified_lines:
        print("\n[bold yellow]Modified:[/bold yellow]")
        for line in report.modified_lines[:10]:
            print(f"  - {line[:200]}")

    if report.weakened_negatives:
        print("\n[bold red]Weakened Negative Constraints:[/bold red]")
        for line in report.weakened_negatives[:10]:
            print(f"  - {line[:200]}")

    if report.warnings:
        print("\n[bold yellow]Warnings:[/bold yellow]")
        for w in report.warnings:
            print(f"  - {w}")


def _print_validation_markdown(report: ValidationReport) -> None:
    """Print validation report as Markdown."""
    lines = [
        "# TokenSentry Validation Report",
        f"**Status:** {'PASS' if report.passed else 'REVIEW REQUIRED'}",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Summary",
        f"- Preserved: {len(report.preserved_lines)}",
        f"- Missing: {len(report.missing_lines)}",
        f"- Modified: {len(report.modified_lines)}",
        f"- Weakened: {len(report.weakened_negatives)}",
        "",
    ]

    if report.missing_lines:
        lines.append("## Missing Requirements")
        for line in report.missing_lines:
            lines.append(f"- {line}")
        lines.append("")

    if report.weakened_negatives:
        lines.append("## Weakened Negative Constraints")
        for line in report.weakened_negatives:
            lines.append(f"- {line}")
        lines.append("")

    if report.warnings:
        lines.append("## Warnings")
        for w in report.warnings:
            lines.append(f"- {w}")
        lines.append("")

    print("\n".join(lines))


@app.command()
def analyze(
    prompt_file: Annotated[Path, ANALYZE_FILE_ARG],
    tokenizer: Annotated[str | None, TOKENIZER_OPTION] = None,
    format: Annotated[str, FORMAT_OPTION] = "terminal",
    list_tokenizers: Annotated[bool, LIST_TOKENIZERS_FLAG] = False,
) -> None:
    """Analyze a prompt file for structure, quality, and token usage."""
    if list_tokenizers:
        _list_tokenizers()
        return

    content = _read_file(prompt_file)
    report = analyze_prompt(content, tokenizer_name=tokenizer, prompt_id=prompt_file.stem)
    _print_analysis_report(report, format)


@app.command()
def optimize(
    prompt_file: Annotated[Path, OPTIMIZE_FILE_ARG],
    output: Annotated[Path, OUTPUT_OPTION] = Path("optimized-prompt.md"),
    tokenizer: Annotated[str | None, TOKENIZER_OPTION] = None,
    profile: Annotated[OptimizationProfile, PROFILE_OPTION] = OptimizationProfile.CONSERVATIVE,
    format: Annotated[str, FORMAT_OPTION] = "terminal",
) -> None:
    """Optimize a prompt file with the specified profile."""
    content = _read_file(prompt_file)

    # First analyze to get technical literals
    analysis = analyze_prompt(content, tokenizer_name=tokenizer)

    result = optimize_prompt(
        content,
        profile=profile,
        tokenizer_name=tokenizer,
        technical_literals=analysis.technical_literals,
    )

    _write_file(output, result.optimized)
    print(f"[green]Optimized prompt written to:[/green] {output}")
    _print_optimization_result(result, format)


@app.command()
def validate(
    original_file: Annotated[Path, VALIDATE_ORIGINAL_ARG],
    optimized_file: Annotated[Path, VALIDATE_OPTIMIZED_ARG],
    tokenizer: Annotated[str | None, TOKENIZER_OPTION] = None,
    format: Annotated[str, FORMAT_OPTION] = "terminal",
) -> None:
    """Validate an optimized prompt against the original."""
    original = _read_file(original_file)
    optimized = _read_file(optimized_file)

    # Analyze original to get requirements and literals
    analysis = analyze_prompt(original, tokenizer_name=tokenizer)

    report = validate_prompt(
        original,
        optimized,
        original_requirements=analysis.requirements,
        original_literals=analysis.technical_literals,
    )

    _print_validation_report(report, format)


@app.command()
def tokenizers(list_tokenizers: Annotated[bool, LIST_TOKENIZERS_FLAG] = True) -> None:
    """List available tokenizers."""
    _list_tokenizers()


def _list_tokenizers() -> None:
    """List available tokenizers."""
    tokenizers = list_tokenizers()
    print("[bold]Available tokenizers:[/bold]")
    for t in tokenizers:
        print(f"  - {t}")


@app.command()
def version() -> None:
    """Show version information."""
    from tokensentry import __version__
    print(f"TokenSentry {__version__}")


if __name__ == "__main__":
    app()