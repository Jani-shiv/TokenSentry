"""Reports package for TokenSentry."""

from __future__ import annotations

from tokensentry.reports.json import (
    JSONExporter,
    export_analysis_json,
    export_optimization_json,
    export_validation_json,
    export_combined_json,
)
from tokensentry.reports.markdown import (
    MarkdownExporter,
    export_analysis_markdown,
    export_optimization_markdown,
    export_validation_markdown,
    export_combined_markdown,
)
from tokensentry.reports.terminal import (
    TerminalExporter,
    print_analysis,
    print_optimization,
    print_validation,
)

__all__ = [
    # JSON
    "JSONExporter",
    "export_analysis_json",
    "export_optimization_json",
    "export_validation_json",
    "export_combined_json",
    # Markdown
    "MarkdownExporter",
    "export_analysis_markdown",
    "export_optimization_markdown",
    "export_validation_markdown",
    "export_combined_markdown",
    # Terminal
    "TerminalExporter",
    "print_analysis",
    "print_optimization",
    "print_validation",
]