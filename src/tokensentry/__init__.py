"""TokenSentry - Local-first prompt analysis, optimization, and validation toolkit."""

from __future__ import annotations

from tokensentry.cli import app
from tokensentry.config import get_config, get_settings, validate_file_path, validate_prompt_content
from tokensentry.core import analyze_prompt, optimize_prompt, validate_prompt
from tokensentry.models import (
    AnalysisReport,
    Config,
    Finding,
    OptimizationProfile,
    OptimizationResult,
    PromptStats,
    Requirement,
    TechnicalLiteral,
    TokenCountKind,
    TokenizerInfo,
    ValidationReport,
)
from tokensentry.tokenizers import (
    BaseTokenizer,
    CharacterEstimateTokenizer,
    get_tokenizer,
    list_tokenizers,
    register_tokenizer,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # CLI
    "app",
    # Config
    "get_config",
    "get_settings",
    "validate_file_path",
    "validate_prompt_content",
    # Core engines
    "analyze_prompt",
    "optimize_prompt",
    "validate_prompt",
    # Models
    "AnalysisReport",
    "Config",
    "Finding",
    "OptimizationProfile",
    "OptimizationResult",
    "PromptStats",
    "Requirement",
    "TechnicalLiteral",
    "TokenCountKind",
    "TokenizerInfo",
    "ValidationReport",
    # Tokenizers
    "BaseTokenizer",
    "CharacterEstimateTokenizer",
    "get_tokenizer",
    "list_tokenizers",
    "register_tokenizer",
]