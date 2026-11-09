"""Analysis module package."""

from __future__ import annotations

# Import analyzer modules to trigger registration
from tokensentry.analysis import (  # noqa: F401,E402
    ambiguity,
    complexity,
    contradictions,
    quality,
    redundancy,
    security,
    structure,
)
from tokensentry.analysis.registry import AnalyzerRegistry, BaseAnalyzer, registry

__all__ = ["BaseAnalyzer", "AnalyzerRegistry", "registry"]