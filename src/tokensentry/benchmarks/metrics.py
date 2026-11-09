"""Evaluation metrics for TokenSentry benchmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptMetrics:
    """Metrics for a single prompt evaluation."""

    prompt_id: str
    original_tokens: int
    optimized_tokens: int
    token_delta: int
    token_reduction_pct: float

    # Preservation metrics
    requirements_total: int = 0
    requirements_preserved: int = 0
    requirements_missing: int = 0
    requirements_weakened: int = 0
    preservation_rate: float = 0.0

    # Literal preservation
    literals_total: int = 0
    literals_preserved: int = 0
    literals_missing: int = 0
    literal_preservation_rate: float = 0.0

    # Quality scores
    clarity_score: float | None = None
    completeness_score: float | None = None
    structure_score: float | None = None
    conciseness_score: float | None = None
    actionability_score: float | None = None
    overall_quality_score: float | None = None

    # Performance
    optimization_time_ms: float = 0.0
    validation_time_ms: float = 0.0

    # Issues
    warnings_count: int = 0
    errors_count: int = 0


@dataclass
class AggregateMetrics:
    """Aggregated metrics across multiple prompts."""

    total_prompts: int = 0
    successful_optimizations: int = 0
    failed_optimizations: int = 0

    # Token metrics
    avg_token_reduction_pct: float = 0.0
    median_token_reduction_pct: float = 0.0
    total_tokens_saved: int = 0

    # Preservation metrics
    avg_preservation_rate: float = 0.0
    avg_literal_preservation_rate: float = 0.0
    prompts_with_zero_missing: int = 0
    prompts_with_zero_weakened: int = 0

    # Quality metrics
    avg_quality_score: float = 0.0
    quality_improved: int = 0
    quality_degraded: int = 0

    # Performance
    avg_optimization_time_ms: float = 0.0
    avg_validation_time_ms: float = 0.0

    # By profile
    by_profile: dict[str, dict[str, Any]] = field(default_factory=dict)

    # By category
    by_category: dict[str, dict[str, Any]] = field(default_factory=dict)

    # By difficulty
    by_difficulty: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Complete benchmark result for a single prompt."""

    prompt_id: str
    prompt_name: str
    category: str
    difficulty: str
    profile: str
    metrics: PromptMetrics
    success: bool
    error: str | None = None


def compute_prompt_metrics(
    prompt_id: str,
    original_tokens: int,
    optimized_tokens: int,
    requirements_total: int,
    requirements_preserved: int,
    requirements_missing: int,
    requirements_weakened: int,
    literals_total: int,
    literals_preserved: int,
    literals_missing: int,
    quality_scores: dict[str, float] | None = None,
    optimization_time_ms: float = 0.0,
    validation_time_ms: float = 0.0,
    warnings_count: int = 0,
    errors_count: int = 0,
) -> PromptMetrics:
    """Compute metrics for a single prompt."""
    token_delta = original_tokens - optimized_tokens
    token_reduction_pct = (token_delta / original_tokens * 100) if original_tokens > 0 else 0.0

    preservation_rate = (requirements_preserved / requirements_total * 100) if requirements_total > 0 else 100.0
    literal_preservation_rate = (literals_preserved / literals_total * 100) if literals_total > 0 else 100.0

    return PromptMetrics(
        prompt_id=prompt_id,
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        token_delta=token_delta,
        token_reduction_pct=token_reduction_pct,
        requirements_total=requirements_total,
        requirements_preserved=requirements_preserved,
        requirements_missing=requirements_missing,
        requirements_weakened=requirements_weakened,
        preservation_rate=preservation_rate,
        literals_total=literals_total,
        literals_preserved=literals_preserved,
        literals_missing=literals_missing,
        literal_preservation_rate=literal_preservation_rate,
        clarity_score=quality_scores.get("clarity") if quality_scores else None,
        completeness_score=quality_scores.get("completeness") if quality_scores else None,
        structure_score=quality_scores.get("structure") if quality_scores else None,
        conciseness_score=quality_scores.get("conciseness") if quality_scores else None,
        actionability_score=quality_scores.get("actionability") if quality_scores else None,
        overall_quality_score=quality_scores.get("overall") if quality_scores else None,
        optimization_time_ms=optimization_time_ms,
        validation_time_ms=validation_time_ms,
        warnings_count=warnings_count,
        errors_count=errors_count,
    )


def aggregate_metrics(results: list[BenchmarkResult]) -> AggregateMetrics:
    """Aggregate metrics across multiple benchmark results."""
    if not results:
        return AggregateMetrics()

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    agg = AggregateMetrics(
        total_prompts=len(results),
        successful_optimizations=len(successful),
        failed_optimizations=len(failed),
    )

    if not successful:
        return agg

    # Token metrics
    reductions = [r.metrics.token_reduction_pct for r in successful]
    agg.avg_token_reduction_pct = sum(reductions) / len(reductions)
    agg.median_token_reduction_pct = sorted(reductions)[len(reductions) // 2]
    agg.total_tokens_saved = sum(r.metrics.token_delta for r in successful)

    # Preservation metrics
    preservation_rates = [r.metrics.preservation_rate for r in successful]
    agg.avg_preservation_rate = sum(preservation_rates) / len(preservation_rates)

    literal_rates = [r.metrics.literal_preservation_rate for r in successful]
    agg.avg_literal_preservation_rate = sum(literal_rates) / len(literal_rates)

    agg.prompts_with_zero_missing = sum(1 for r in successful if r.metrics.requirements_missing == 0)
    agg.prompts_with_zero_weakened = sum(1 for r in successful if r.metrics.requirements_weakened == 0)

    # Quality metrics
    quality_scores = [r.metrics.overall_quality_score for r in successful if r.metrics.overall_quality_score is not None]
    if quality_scores:
        agg.avg_quality_score = sum(quality_scores) / len(quality_scores)

    # Performance
    opt_times = [r.metrics.optimization_time_ms for r in successful if r.metrics.optimization_time_ms > 0]
    if opt_times:
        agg.avg_optimization_time_ms = sum(opt_times) / len(opt_times)

    val_times = [r.metrics.validation_time_ms for r in successful if r.metrics.validation_time_ms > 0]
    if val_times:
        agg.avg_validation_time_ms = sum(val_times) / len(val_times)

    # By profile
    profiles = {}
    for r in successful:
        profile = r.profile
        if profile not in profiles:
            profiles[profile] = {"count": 0, "avg_reduction": 0.0, "avg_preservation": 0.0}
        p = profiles[profile]
        p["count"] += 1
        p["avg_reduction"] = (p["avg_reduction"] * (p["count"] - 1) + r.metrics.token_reduction_pct) / p["count"]
        p["avg_preservation"] = (p["avg_preservation"] * (p["count"] - 1) + r.metrics.preservation_rate) / p["count"]
    agg.by_profile = profiles

    # By category
    categories = {}
    for r in successful:
        cat = r.category
        if cat not in categories:
            categories[cat] = {"count": 0, "avg_reduction": 0.0, "avg_preservation": 0.0}
        c = categories[cat]
        c["count"] += 1
        c["avg_reduction"] = (c["avg_reduction"] * (c["count"] - 1) + r.metrics.token_reduction_pct) / c["count"]
        c["avg_preservation"] = (c["avg_preservation"] * (c["count"] - 1) + r.metrics.preservation_rate) / c["count"]
    agg.by_category = categories

    # By difficulty
    difficulties = {}
    for r in successful:
        diff = r.difficulty
        if diff not in difficulties:
            difficulties[diff] = {"count": 0, "avg_reduction": 0.0, "avg_preservation": 0.0}
        d = difficulties[diff]
        d["count"] += 1
        d["avg_reduction"] = (d["avg_reduction"] * (d["count"] - 1) + r.metrics.token_reduction_pct) / d["count"]
        d["avg_preservation"] = (d["avg_preservation"] * (d["count"] - 1) + r.metrics.preservation_rate) / d["count"]
    agg.by_difficulty = difficulties

    return agg


def format_metrics_summary(agg: AggregateMetrics) -> str:
    """Format aggregate metrics as human-readable summary."""
    lines = [
        "=" * 60,
        "TOKENSENTRY BENCHMARK SUMMARY",
        "=" * 60,
        f"Total Prompts: {agg.total_prompts}",
        f"Successful: {agg.successful_optimizations}",
        f"Failed: {agg.failed_optimizations}",
        "",
        "TOKEN REDUCTION:",
        f"  Average: {agg.avg_token_reduction_pct:.1f}%",
        f"  Median: {agg.median_token_reduction_pct:.1f}%",
        f"  Total Saved: {agg.total_tokens_saved:,} tokens",
        "",
        "PRESERVATION:",
        f"  Avg Requirement Preservation: {agg.avg_preservation_rate:.1f}%",
        f"  Avg Literal Preservation: {agg.avg_literal_preservation_rate:.1f}%",
        f"  Zero Missing Requirements: {agg.prompts_with_zero_missing}/{agg.successful_optimizations}",
        f"  Zero Weakened Constraints: {agg.prompts_with_zero_weakened}/{agg.successful_optimizations}",
        "",
        "QUALITY:",
        f"  Avg Quality Score: {agg.avg_quality_score:.2f}",
        "",
        "PERFORMANCE:",
        f"  Avg Optimization Time: {agg.avg_optimization_time_ms:.1f}ms",
        f"  Avg Validation Time: {agg.avg_validation_time_ms:.1f}ms",
        "",
    ]

    if agg.by_profile:
        lines.append("BY PROFILE:")
        for profile, data in agg.by_profile.items():
            lines.append(f"  {profile}: {data['count']} prompts, "
                         f"avg reduction {data['avg_reduction']:.1f}%, "
                         f"avg preservation {data['avg_preservation']:.1f}%")

    if agg.by_category:
        lines.append("")
        lines.append("BY CATEGORY:")
        for cat, data in agg.by_category.items():
            lines.append(f"  {cat}: {data['count']} prompts, "
                         f"avg reduction {data['avg_reduction']:.1f}%, "
                         f"avg preservation {data['avg_preservation']:.1f}%")

    lines.append("=" * 60)
    return "\n".join(lines)