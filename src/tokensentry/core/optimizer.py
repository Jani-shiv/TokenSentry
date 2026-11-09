"""Core optimizer - delegates to optimization module."""

from __future__ import annotations

from tokensentry.models import (
    OptimizationProfile,
    OptimizationResult,
    TechnicalLiteral,
)
from tokensentry.optimization import optimize_prompt

# Re-export for backward compatibility
__all__ = ["optimize_prompt", "OptimizationProfile", "OptimizationResult", "TechnicalLiteral"]