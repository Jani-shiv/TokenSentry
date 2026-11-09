"""Benchmark package for TokenSentry evaluation."""

from __future__ import annotations

from tokensentry.benchmarks.datasets import (
    BENCHMARK_PROMPTS,
    CATEGORIES,
    DIFFICULTIES,
    BenchmarkPrompt,
    get_all_prompts,
    get_prompts_by_category,
    get_prompts_by_difficulty,
)
from tokensentry.benchmarks.metrics import (
    AggregateMetrics,
    BenchmarkResult,
    PromptMetrics,
    aggregate_metrics,
    compute_prompt_metrics,
    format_metrics_summary,
)
from tokensentry.benchmarks.reports import (
    generate_json_report,
    generate_markdown_report,
    save_report,
)
from tokensentry.benchmarks.runner import BenchmarkRunner, run_benchmark

__all__ = [
    # Datasets
    "BenchmarkPrompt",
    "BENCHMARK_PROMPTS",
    "CATEGORIES",
    "DIFFICULTIES",
    "get_all_prompts",
    "get_prompts_by_category",
    "get_prompts_by_difficulty",
    # Metrics
    "AggregateMetrics",
    "BenchmarkResult",
    "PromptMetrics",
    "aggregate_metrics",
    "compute_prompt_metrics",
    "format_metrics_summary",
    # Reports
    "generate_json_report",
    "generate_markdown_report",
    "save_report",
    # Runner
    "BenchmarkRunner",
    "run_benchmark",
]