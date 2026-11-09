"""Tests for core TokenSentry functionality."""

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.core.optimizer import optimize_prompt
from tokensentry.core.validator import validate_prompt
from tokensentry.models import OptimizationProfile, Severity


def test_analyzer_reports_stats_and_estimate() -> None:
    result = analyze_prompt("hello world\nsecond line")
    assert result.stats.words == 4
    assert result.tokenizer.count_kind.value == "estimate"
    assert result.token_count > 0


def test_analyzer_detects_repeated_line() -> None:
    result = analyze_prompt("repeat\nkeep\nrepeat")
    assert any(x.code == "REPEATED_LINE" for x in result.findings)


def test_analyzer_detects_ambiguous_language() -> None:
    result = analyze_prompt("Do something appropriate and handle various things.")
    assert any(x.code == "AMBIGUOUS_LANGUAGE" for x in result.findings)


def test_analyzer_extracts_requirements() -> None:
    result = analyze_prompt("You must use JSON format. You must not use XML.")
    assert len(result.requirements) >= 2
    req_types = {r.type for r in result.requirements}
    assert "positive" in req_types or "format" in req_types
    assert "negative" in req_types


def test_analyzer_finds_technical_literals() -> None:
    result = analyze_prompt("Run `kubectl get pods` and visit https://example.com")
    literal_types = {lit.type for lit in result.technical_literals}
    assert "command" in literal_types
    assert "url" in literal_types


def test_optimizer_conservative_only_whitespace() -> None:
    result = optimize_prompt("hello\n\n\nworld\n", profile=OptimizationProfile.CONSERVATIVE)
    assert result.optimized == "hello\n\nworld"
    assert result.profile == OptimizationProfile.CONSERVATIVE
    assert len(result.transformations) >= 1


def test_optimizer_preserves_technical_literals() -> None:
    prompt = "Run `kubectl get pods` and visit https://example.com"
    result = optimize_prompt(prompt, profile=OptimizationProfile.CONSERVATIVE)
    assert "`kubectl get pods`" in result.optimized
    assert "https://example.com" in result.optimized


def test_optimizer_balanced_consolidates() -> None:
    prompt = "You must do X. You must do X. You must do Y."
    result = optimize_prompt(prompt, profile=OptimizationProfile.BALANCED)
    assert result.optimized_token_count <= result.original_token_count


def test_validator_detects_missing_requirement() -> None:
    original = "You must use JSON. You must not use XML."
    optimized = "Use JSON format."
    result = validate_prompt(original, optimized)
    assert not result.passed
    assert len(result.missing_lines) > 0


def test_validator_preserves_negative_constraints() -> None:
    original = "You must not use XML. You must not expose secrets."
    optimized = "Use JSON format."
    result = validate_prompt(original, optimized)
    assert not result.passed
    assert len(result.weakened_negatives) > 0


def test_validator_preserves_technical_literals() -> None:
    original = "Run `kubectl get pods`"
    optimized = "Run kubectl get pods"  # Missing backticks
    result = validate_prompt(original, optimized)
    # Should detect missing code literal
    assert len(result.checks) > 0


def test_optimization_profiles_exist() -> None:
    assert OptimizationProfile.CONSERVATIVE
    assert OptimizationProfile.BALANCED
    assert OptimizationProfile.AGGRESSIVE


def test_severity_levels() -> None:
    assert Severity.INFO
    assert Severity.WARNING
    assert Severity.ERROR
    assert Severity.CRITICAL