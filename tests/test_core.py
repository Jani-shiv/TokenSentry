"""Tests for core TokenSentry functionality."""


from tokensentry.core.analyzer import analyze_prompt
from tokensentry.core.optimizer import optimize_prompt
from tokensentry.core.validator import validate_prompt
from tokensentry.models import OptimizationProfile, PreservationStatus, Severity
from tokensentry.validation import (
    PreservationValidator,
    compare_structures,
    detect_output_format,
    validate_json_structure,
    validate_yaml_structure,
)


def test_analyzer_reports_stats_and_estimate() -> None:
    result = analyze_prompt("hello world\nsecond line")
    assert result.stats.words == 4
    assert result.tokenizer.count_kind.value == "estimate"
    assert result.token_count > 0


def test_analyzer_detects_repeated_line() -> None:
    result = analyze_prompt("repeat\nkeep\nrepeat")
    # New modular analyzer uses DUPLICATE_LINE
    assert any(x.code == "DUPLICATE_LINE" for x in result.findings)


def test_analyzer_detects_ambiguous_language() -> None:
    result = analyze_prompt("Do something appropriate and handle various things.")
    # New modular analyzer uses AMBIGUOUS_VAGUE_QUANTIFIER, AMBIGUOUS_CONDITIONAL_WITHOUT_CRITERIA
    assert any("AMBIGUOUS" in x.code for x in result.findings)


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


# ============================================================================
# NEW VALIDATION MODULE TESTS
# ============================================================================

def test_detect_output_format() -> None:
    assert detect_output_format("Return JSON output") == "json"
    assert detect_output_format("Output as YAML") == "yaml"
    assert detect_output_format("Return XML") == "xml"
    assert detect_output_format("CSV format") == "csv"
    assert detect_output_format("Markdown please") == "markdown"
    assert detect_output_format("Just text") is None


def test_validate_json_structure_valid() -> None:
    errors = validate_json_structure('{"name": "test", "value": 123}')
    assert len(errors) == 0


def test_validate_json_structure_invalid() -> None:
    errors = validate_json_structure('{"name": "test", "value": }')
    assert len(errors) > 0
    assert "Invalid JSON" in str(errors[0])


def test_validate_json_with_schema() -> None:
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }
    errors = validate_json_structure('{"name": "test"}', schema)
    assert len(errors) == 0

    errors = validate_json_structure('{"age": 25}', schema)
    assert len(errors) > 0
    assert "Missing required field" in str(errors[0])


def test_validate_yaml_structure_valid() -> None:
    errors = validate_yaml_structure("name: test\nvalue: 123")
    assert len(errors) == 0


def test_validate_yaml_structure_invalid() -> None:
    errors = validate_yaml_structure("name: test\n  value: [1, 2,")
    assert len(errors) > 0


def test_compare_structures_json() -> None:
    original = '{"name": "test", "items": [1, 2, 3]}'
    optimized = '{"name": "test", "items": [1, 2]}'
    errors = compare_structures(original, optimized, "json")
    # Both valid JSON, no structural errors
    assert len(errors) == 0


def test_compare_structures_json_broken() -> None:
    original = '{"name": "test"}'
    optimized = '{"name": "test",}'  # Trailing comma - invalid JSON
    errors = compare_structures(original, optimized, "json")
    assert len(errors) > 0
    assert "Optimized introduced structural errors" in str(errors[0])


def test_preservation_validator_requirements() -> None:
    validator = PreservationValidator()
    original = "You must use JSON. You must not use XML."
    optimized = "Use JSON format."

    checks = validator.validate(original, optimized)

    # Should have checks for both requirements
    assert len(checks) >= 2

    # Check that positive requirement is detected
    positive_checks = [c for c in checks if c.requirement.type == "positive"]
    assert len(positive_checks) > 0

    # Check that negative requirement is detected
    negative_checks = [c for c in checks if c.requirement.type == "negative"]
    assert len(negative_checks) > 0


def test_preservation_validator_literals() -> None:
    validator = PreservationValidator()
    original = "Run `kubectl get pods` and visit https://example.com"
    optimized = "Run kubectl get pods and visit https://example.com"

    checks = validator.validate(original, optimized)

    # Should detect missing code literal (backticks removed)
    code_checks = [c for c in checks if "code" in c.requirement.text.lower()]
    assert len(code_checks) > 0


def test_preservation_validator_negative_weakening() -> None:
    validator = PreservationValidator()
    original = "You must not use XML. You must not expose secrets."
    optimized = "Use JSON format."

    checks = validator.validate(original, optimized)

    # Should detect weakened negative constraints
    weakened = [c for c in checks if c.status.value == "weakened"]
    assert len(weakened) > 0


def test_preservation_validator_exact_preservation() -> None:
    validator = PreservationValidator()
    original = "Run `kubectl get pods`"
    optimized = "Run `kubectl get pods`"

    checks = validator.validate(original, optimized)

    # Should find exact preservation
    exact = [c for c in checks if c.status == PreservationStatus.EXACT]
    assert len(exact) > 0


def test_preservation_validator_schema_preservation() -> None:
    validator = PreservationValidator()
    original = 'Return JSON: {"name": "test", "items": [1, 2, 3]}'
    optimized = 'Return JSON: {"name": "test", "items": [1, 2]}'

    checks = validator.validate(original, optimized)

    # Should have checks
    assert len(checks) > 0


def test_preservation_status_enum() -> None:
    assert PreservationStatus.EXACT == "exact"
    assert PreservationStatus.STRUCTURAL == "structural"
    assert PreservationStatus.PROBABLE == "probable"
    assert PreservationStatus.UNCERTAIN == "uncertain"
    assert PreservationStatus.MISSING == "missing"
    assert PreservationStatus.MODIFIED == "modified"
    assert PreservationStatus.WEAKENED == "weakened"


def test_validate_prompt_enhanced() -> None:
    original = "You must use JSON. You must not use XML."
    optimized = "Use JSON format."

    from tokensentry.validation import validate_prompt_enhanced
    checks = validate_prompt_enhanced(original, optimized)

    assert len(checks) > 0
    # Should detect missing negative constraint
    missing = [c for c in checks if c.status == PreservationStatus.MISSING]
    assert len(missing) > 0


def test_validator_integration_with_analyzer() -> None:
    """Test validator works with analyzer output."""
    original = "You must use JSON format. You must not use XML. Run `kubectl get pods`."
    optimized = "Use JSON. Run kubectl get pods."

    # Analyze original to get requirements and literals
    analysis = analyze_prompt(original)

    result = validate_prompt(
        original,
        optimized,
        original_requirements=analysis.requirements,
        original_literals=analysis.technical_literals,
    )

    assert result.checks is not None
    assert len(result.checks) > 0


def test_validator_detailed_checks() -> None:
    original = "You must use JSON. You must not use XML. You must include exactly 5 items."
    optimized = "Use JSON. Include items."

    result = validate_prompt(original, optimized)

    assert not result.passed
    assert len(result.missing_lines) > 0
    # Should detect missing value constraint (exactly 5)
    value_checks = [c for c in result.checks if c.requirement.type == "value"]
    assert len(value_checks) > 0


def test_validator_summary_counts() -> None:
    original = "You must use JSON. You must not use XML. Run `kubectl get pods`."
    optimized = "Use JSON. Run `kubectl get pods`."

    result = validate_prompt(original, optimized)

    summary = result.summary
    assert "total_checks" in summary
    assert "exact" in summary
    assert "missing" in summary
    assert "weakened" in summary
    assert summary["total_checks"] > 0