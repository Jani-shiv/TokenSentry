"""Analysis module package."""

from __future__ import annotations

from tokensentry.analysis.registry import BaseAnalyzer, AnalyzerRegistry, registry

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

__all__ = ["BaseAnalyzer", "AnalyzerRegistry", "registry"]