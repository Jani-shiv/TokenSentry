"""Configuration management for TokenSentry."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tokensentry.models import Config, OptimizationProfile


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""

    model_config = SettingsConfigDict(
        env_prefix="TOKENSENTRY_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core settings
    max_prompt_size: int = Field(default=10_485_760, ge=1024)
    max_line_length: int = Field(default=10_000, ge=100)
    default_tokenizer: str = "character-estimate"
    default_optimization_profile: OptimizationProfile = OptimizationProfile.CONSERVATIVE
    enable_security_checks: bool = True
    enable_quality_scoring: bool = True
    report_schema_version: str = "1.0"
    timeout_seconds: int = Field(default=30, ge=1, le=300)

    # Path security
    allowed_read_paths: list[Path] = Field(default_factory=list)
    denied_patterns: list[str] = Field(
        default_factory=lambda: [
            "..",
            "~",
            "$",
            "%",
            "passwd",
            "shadow",
            "ssh",
            ".aws",
            ".ssh",
            "id_rsa",
            "id_ed25519",
            ".env",
            "secret",
            "credential",
            "token",
            "api_key",
        ]
    )

    # Tokenizer settings
    tiktoken_cache_dir: Path | None = None
    hf_tokenizer_cache_dir: Path | None = None
    hf_offline_mode: bool = False

    # Skill settings
    skill_directories: list[Path] = Field(default_factory=list)
    auto_load_skills: bool = True

    # Benchmark settings
    benchmark_corpus_path: Path | None = None
    benchmark_results_path: Path | None = None

    # Optional API settings (for future use)
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_enabled: bool = False
    api_cors_origins: list[str] = Field(default_factory=list)

    def to_config(self) -> Config:
        """Convert to runtime Config model."""
        return Config(
            max_prompt_size=self.max_prompt_size,
            max_line_length=self.max_line_length,
            default_tokenizer=self.default_tokenizer,
            default_optimization_profile=self.default_optimization_profile,
            enable_security_checks=self.enable_security_checks,
            enable_quality_scoring=self.enable_quality_scoring,
            report_schema_version=self.report_schema_version,
            allowed_read_paths=self.allowed_read_paths,
            denied_patterns=self.denied_patterns,
            timeout_seconds=self.timeout_seconds,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_config() -> Config:
    """Get runtime configuration."""
    return get_settings().to_config()


def validate_file_path(path: Path, config: Config | None = None) -> Path:
    """Validate file path for security.

    Args:
        path: Path to validate
        config: Optional config, uses global if not provided

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path is not allowed
    """
    if config is None:
        config = get_config()

    # Resolve path
    try:
        resolved = path.resolve()
    except Exception as e:
        raise ValueError(f"Invalid path: {e}") from e

    # Check denied patterns
    path_str = str(resolved).lower()
    for pattern in config.denied_patterns:
        if pattern.lower() in path_str:
            raise ValueError(f"Path contains denied pattern: {pattern}")

    # Check allowed paths if configured
    if config.allowed_read_paths:
        allowed = False
        for allowed_path in config.allowed_read_paths:
            try:
                if resolved.is_relative_to(allowed_path.resolve()):
                    allowed = True
                    break
            except Exception:
                continue
        if not allowed:
            raise ValueError(f"Path not in allowed directories: {resolved}")

    # Check file exists and is readable
    if not resolved.exists():
        raise ValueError(f"File does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Path is not a file: {resolved}")

    # Check size
    try:
        size = resolved.stat().st_size
        if size > config.max_prompt_size:
            raise ValueError(f"File too large: {size} bytes (max {config.max_prompt_size})")
    except OSError as e:
        raise ValueError(f"Cannot stat file: {e}") from e

    return resolved


def validate_prompt_content(content: str, config: Config | None = None) -> str:
    """Validate and sanitize prompt content.

    Args:
        content: Prompt text
        config: Optional config

    Returns:
        Validated content

    Raises:
        ValueError: If content is invalid
    """
    if config is None:
        config = get_config()

    if not content:
        raise ValueError("Prompt content is empty")

    if len(content) > config.max_prompt_size:
        raise ValueError(f"Prompt too large: {len(content)} chars (max {config.max_prompt_size})")

    # Check for null bytes and control characters (except newline, tab)
    for i, ch in enumerate(content):
        if ch == "\x00":
            raise ValueError(f"Null byte at position {i}")
        if ord(ch) < 32 and ch not in ("\n", "\r", "\t"):
            raise ValueError(f"Control character at position {i}: U+{ord(ch):04X}")

    # Check line lengths
    for i, line in enumerate(content.splitlines(), 1):
        if len(line) > config.max_line_length:
            raise ValueError(f"Line {i} exceeds max length: {len(line)} > {config.max_line_length}")

    return content