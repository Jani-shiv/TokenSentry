"""Benchmark reporting utilities."""

from __future__ import annotations

import json
from typing import Any

from tokensentry.benchmarks.metrics import AggregateMetrics, BenchmarkResult, format_metrics_summary


def generate_json_report(
    agg: AggregateMetrics,
    results: list[BenchmarkResult] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Generate JSON benchmark report."""
    report = {
        "schema_version": "1.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "summary": agg.__dict__,
        "metadata": metadata or {},
    }

    if results:
        report["results"] = [r.__dict__ for r in results]

    return json.dumps(report, indent=2, default=str)


def generate_markdown_report(
    agg: AggregateMetrics,
    results: list[BenchmarkResult] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Generate Markdown benchmark report."""
    lines = [
        "# TokenSentry Benchmark Report",
        "",
        f"**Generated:** {__import__('datetime').datetime.now().isoformat()}",
        "**Schema Version:** 1.0",
        "",
    ]

    if metadata:
        lines.append("## Configuration")
        for k, v in metadata.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    lines.append(format_metrics_summary(agg))

    if results:
        lines.append("## Detailed Results")
        lines.append("")
        lines.append("| Prompt | Category | Difficulty | Profile | Tokens | Reduction | Preservation | Status |")
        lines.append("|--------|----------|------------|---------|--------|-----------|--------------|--------|")

        for r in results:
            m = r.metrics
            status = "✅" if r.success else "❌"
            tokens = f"{m.original_tokens}→{m.optimized_tokens}"
            reduction = f"{m.token_reduction_pct:+.1f}%"
            preservation = f"{m.preservation_rate:.1f}%"
            lines.append(f"| {r.prompt_name} | {r.category} | {r.difficulty} | {r.profile} | {tokens} | {reduction} | {preservation} | {status} |")

    return "\n".join(lines)


def save_report(
    agg: AggregateMetrics,
    results: list[BenchmarkResult] | None = None,
    output_dir: str = ".",
    formats: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> list[str]:
    """Save benchmark report in multiple formats."""
    from pathlib import Path

    formats = formats or ["json", "markdown"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"benchmark_{timestamp}"

    saved = []

    if "json" in formats:
        json_path = Path(output_dir) / f"{base_name}.json"
        json_path.write_text(generate_json_report(agg, results, metadata))
        saved.append(str(json_path))

    if "markdown" in formats:
        md_path = Path(output_dir) / f"{base_name}.md"
        md_path.write_text(generate_markdown_report(agg, results, metadata))
        saved.append(str(md_path))

    if "summary" in formats:
        txt_path = Path(output_dir) / f"{base_name}_summary.txt"
        txt_path.write_text(format_metrics_summary(agg))
        saved.append(str(txt_path))

    return saved