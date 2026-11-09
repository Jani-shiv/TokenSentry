"""Benchmark runner for TokenSentry evaluation."""

from __future__ import annotations

import time
from typing import Any

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.core.optimizer import optimize_prompt
from tokensentry.core.validator import validate_prompt
from tokensentry.models import OptimizationProfile
from tokensentry.benchmarks.datasets import BenchmarkPrompt, get_all_prompts
from tokensentry.benchmarks.metrics import (
    AggregateMetrics,
    BenchmarkResult,
    PromptMetrics,
    aggregate_metrics,
    compute_prompt_metrics,
    format_metrics_summary,
)


class BenchmarkRunner:
    """Run benchmarks on TokenSentry optimization pipeline."""

    def __init__(
        self,
        profiles: list[OptimizationProfile] | None = None,
        tokenizer: str = "character-estimate",
        max_prompts: int | None = None,
        categories: list[str] | None = None,
        difficulties: list[str] | None = None,
    ):
        self.profiles = profiles or [
            OptimizationProfile.CONSERVATIVE,
            OptimizationProfile.BALANCED,
            OptimizationProfile.AGGRESSIVE,
        ]
        self.tokenizer = tokenizer
        self.max_prompts = max_prompts
        self.categories = categories
        self.difficulties = difficulties

    def run(self) -> AggregateMetrics:
        """Run all benchmarks and return aggregated metrics."""
        prompts = self._get_prompts()

        if self.max_prompts:
            prompts = prompts[: self.max_prompts]

        results: list[BenchmarkResult] = []

        for prompt in prompts:
            for profile in self.profiles:
                result = self._run_single(prompt, profile)
                results.append(result)

        return aggregate_metrics(results)

    def _get_prompts(self) -> list[BenchmarkPrompt]:
        """Get filtered list of prompts."""
        all_prompts = get_all_prompts()

        if self.categories:
            all_prompts = [p for p in all_prompts if p.category in self.categories]

        if self.difficulties:
            all_prompts = [p for p in all_prompts if p.difficulty in self.difficulties]

        return all_prompts

    def _run_single(self, prompt: BenchmarkPrompt, profile: OptimizationProfile) -> BenchmarkResult:
        """Run benchmark on a single prompt with a profile."""
        start_time = time.perf_counter()

        try:
            # Analyze original
            analysis = analyze_prompt(prompt.prompt, tokenizer_name=self.tokenizer)

            # Optimize
            opt_start = time.perf_counter()
            optimization = optimize_prompt(
                prompt.prompt,
                profile=profile,
                tokenizer_name=self.tokenizer,
                technical_literals=analysis.technical_literals,
            )
            opt_time = (time.perf_counter() - opt_start) * 1000

            # Validate
            val_start = time.perf_counter()
            validation = validate_prompt(
                prompt.prompt,
                optimization.optimized,
                original_requirements=analysis.requirements,
                original_literals=analysis.technical_literals,
            )
            val_time = (time.perf_counter() - val_start) * 1000

            # Compute metrics
            metrics = compute_prompt_metrics(
                prompt_id=prompt.id,
                original_tokens=analysis.token_count,
                optimized_tokens=optimization.optimized_token_count,
                requirements_total=len(analysis.requirements),
                requirements_preserved=len(validation.preserved_lines),
                requirements_missing=len(validation.missing_lines),
                requirements_weakened=len(validation.weakened_negatives),
                literals_total=len(analysis.technical_literals),
                literals_preserved=len([
                    l for l in analysis.technical_literals
                    if any(l.value in optimization.optimized for l in analysis.technical_literals)
                ]),
                literals_missing=len(validation.missing_lines),
                quality_scores=analysis.quality_scores,
                optimization_time_ms=opt_time,
                validation_time_ms=val_time,
                warnings_count=len(optimization.warnings),
                errors_count=0,
            )

            return BenchmarkResult(
                prompt_id=prompt.id,
                prompt_name=prompt.name,
                category=prompt.category,
                difficulty=prompt.difficulty,
                profile=profile.value,
                metrics=metrics,
                success=True,
            )

        except Exception as e:
            return BenchmarkResult(
                prompt_id=prompt.id,
                prompt_name=prompt.name,
                category=prompt.category,
                difficulty=prompt.difficulty,
                profile=profile.value,
                metrics=PromptMetrics(
                    prompt_id=prompt.id,
                    original_tokens=0,
                    optimized_tokens=0,
                    token_delta=0,
                    token_reduction_pct=0.0,
                ),
                success=False,
                error=str(e),
            )


def run_benchmark(
    profiles: list[OptimizationProfile] | None = None,
    tokenizer: str = "character-estimate",
    max_prompts: int | None = None,
    categories: list[str] | None = None,
    difficulties: list[str] | None = None,
    output_file: str | None = None,
) -> AggregateMetrics:
    """Convenience function to run benchmark."""
    runner = BenchmarkRunner(
        profiles=profiles,
        tokenizer=tokenizer,
        max_prompts=max_prompts,
        categories=categories,
        difficulties=difficulties,
    )

    agg = runner.run()

    # Print summary
    print(format_metrics_summary(agg))

    # Save to file if requested
    if output_file:
        import json
        with open(output_file, "w") as f:
            json.dump(agg.__dict__, f, indent=2, default=str)

    return agg


# Import time module
import time
import json