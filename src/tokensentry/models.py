"""Core data models for TokenSentry."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    """Finding severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TokenCountKind(StrEnum):
    """Token count exactness classification."""

    EXACT = "exact"
    ESTIMATE = "estimate"
    APPROXIMATE = "approximate"


class OptimizationProfile(StrEnum):
    """Optimization aggressiveness levels."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class PreservationStatus(StrEnum):
    """Validation preservation status."""

    EXACT = "exact"
    STRUCTURAL = "structural"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"
    MISSING = "missing"
    MODIFIED = "modified"
    WEAKENED = "weakened"


class Finding(BaseModel):
    """Analysis finding with evidence."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    severity: Severity
    message: str = Field(min_length=1)
    evidence: str | None = None
    location: tuple[int, int] | None = None  # (start_line, end_line)
    suggestion: str | None = None


class PromptStats(BaseModel):
    """Basic prompt statistics."""

    model_config = ConfigDict(extra="forbid")

    characters: int = Field(ge=0)
    words: int = Field(ge=0)
    lines: int = Field(ge=0)
    non_empty_lines: int = Field(ge=0)
    avg_line_length: float = Field(ge=0.0, default=0.0)
    max_line_length: int = Field(ge=0, default=0)


class TokenizerInfo(BaseModel):
    """Tokenizer identification and metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    version: str | None = None
    model_id: str | None = None
    encoding: str | None = None
    count_kind: TokenCountKind
    is_exact: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptSection(BaseModel):
    """Parsed prompt section."""

    model_config = ConfigDict(extra="forbid")

    type: str  # heading, code_fence, list, paragraph, schema, etc.
    title: str | None = None
    content: str
    start_line: int
    end_line: int
    level: int | None = None  # for headings
    language: str | None = None  # for code fences
    metadata: dict[str, Any] = Field(default_factory=dict)


class Requirement(BaseModel):
    """Extracted requirement/constraint."""

    model_config = ConfigDict(extra="forbid")

    text: str
    type: Literal["positive", "negative", "value", "format", "schema", "output"]
    source_section: str | None = None
    line_range: tuple[int, int] | None = None
    is_critical: bool = False
    exact_value: str | None = None  # for numeric/string constraints


class TechnicalLiteral(BaseModel):
    """Technical literal that must be preserved byte-for-byte."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "code",
        "command",
        "url",
        "file_path",
        "json",
        "yaml",
        "schema",
        "variable",
        "constant",
    ]
    value: str
    context: str | None = None
    line_range: tuple[int, int] | None = None
    preservation_priority: int = Field(default=10, ge=1, le=10)


class AnalysisReport(BaseModel):
    """Complete prompt analysis report."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    stats: PromptStats
    tokenizer: TokenizerInfo
    token_count: int = Field(ge=0)
    sections: list[PromptSection] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    technical_literals: list[TechnicalLiteral] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    quality_scores: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Transformation(BaseModel):
    """Single optimization transformation."""

    model_config = ConfigDict(extra="forbid")

    type: str
    description: str
    original: str
    optimized: str
    line_range: tuple[int, int] | None = None
    token_delta: int = 0
    risk_level: Severity = Severity.INFO
    preserved_literals: list[str] = Field(default_factory=list)


class OptimizationResult(BaseModel):
    """Optimization result with full traceability."""

    model_config = ConfigDict(extra="forbid")

    original: str
    optimized: str
    profile: OptimizationProfile
    tokenizer: TokenizerInfo
    original_token_count: int = Field(ge=0)
    optimized_token_count: int = Field(ge=0)
    token_delta: int = 0
    transformations: list[Transformation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    preserved_requirements: list[str] = Field(default_factory=list)
    preserved_literals: list[TechnicalLiteral] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def token_reduction_pct(self) -> float:
        if self.original_token_count == 0:
            return 0.0
        return round((self.token_delta / self.original_token_count) * 100, 2)


class ValidationCheck(BaseModel):
    """Single validation check result."""

    model_config = ConfigDict(extra="forbid")

    requirement: Requirement
    status: PreservationStatus
    evidence: str | None = None
    optimized_text: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: str | None = None


class ValidationReport(BaseModel):
    """Validation report comparing original vs optimized."""

    model_config = ConfigDict(extra="forbid")

    passed: bool
    checks: list[ValidationCheck] = Field(default_factory=list)
    preserved_lines: list[str] = Field(default_factory=list)
    missing_lines: list[str] = Field(default_factory=list)
    modified_lines: list[str] = Field(default_factory=list)
    weakened_negatives: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    summary: dict[str, int] = Field(default_factory=dict)


class SkillMetadata(BaseModel):
    """Agent Skill metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^tokensentry-[a-z-]+$")
    version: str
    description: str
    author: str | None = None
    license: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    dependencies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    entry_point: str = "main.py"
    min_tokensentry_version: str = "0.1.0"


class Config(BaseModel):
    """Global configuration."""

    model_config = ConfigDict(extra="forbid")

    max_prompt_size: int = Field(default=10_485_760, ge=1024)  # 10MB
    max_line_length: int = Field(default=10_000, ge=100)
    default_tokenizer: str = "character-estimate"
    default_optimization_profile: OptimizationProfile = OptimizationProfile.CONSERVATIVE
    enable_security_checks: bool = True
    enable_quality_scoring: bool = True
    report_schema_version: str = "1.0"
    allowed_read_paths: list[Path] = Field(default_factory=list)
    denied_patterns: list[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=30, ge=1, le=300)


# Report schemas
class ReportFormat(StrEnum):
    """Output report format."""

    JSON = "json"
    MARKDOWN = "markdown"
    TERMINAL = "terminal"


class AnalysisReportExport(BaseModel):
    """Exportable analysis report."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    timestamp: str
    analysis: AnalysisReport


class OptimizationReportExport(BaseModel):
    """Exportable optimization report."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    timestamp: str
    optimization: OptimizationResult


class ValidationReportExport(BaseModel):
    """Exportable validation report."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    timestamp: str
    validation: ValidationReport