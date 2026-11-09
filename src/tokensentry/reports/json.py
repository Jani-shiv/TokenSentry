"""JSON report exporter for TokenSentry."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from tokensentry.models import (
    AnalysisReport,
    OptimizationResult,
    ValidationReport,
)


class JSONExporter:
    """Export reports as JSON with stable schema."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, pretty: bool = True):
        self.pretty = pretty

    def export_analysis(self, report: AnalysisReport) -> str:
        """Export analysis report as JSON."""
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "timestamp": datetime.now().isoformat(),
            "report_type": "analysis",
            "report": report.model_dump(mode="json"),
        }
        return self._dump(data)

    def export_optimization(self, result: OptimizationResult) -> str:
        """Export optimization result as JSON."""
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "timestamp": datetime.now().isoformat(),
            "report_type": "optimization",
            "report": result.model_dump(mode="json"),
        }
        return self._dump(data)

    def export_validation(self, report: ValidationReport) -> str:
        """Export validation report as JSON."""
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "timestamp": datetime.now().isoformat(),
            "report_type": "validation",
            "report": report.model_dump(mode="json"),
        }
        return self._dump(data)

    def export_combined(
        self,
        analysis: AnalysisReport | None = None,
        optimization: OptimizationResult | None = None,
        validation: ValidationReport | None = None,
    ) -> str:
        """Export combined report as JSON."""
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "timestamp": datetime.now().isoformat(),
            "report_type": "combined",
            "analysis": analysis.model_dump(mode="json") if analysis else None,
            "optimization": optimization.model_dump(mode="json") if optimization else None,
            "validation": validation.model_dump(mode="json") if validation else None,
        }
        return self._dump(data)

    def _dump(self, data: dict[str, Any]) -> str:
        """Dump data as JSON."""
        if self.pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str, separators=(",", ":"))


def export_analysis_json(report: AnalysisReport, pretty: bool = True) -> str:
    """Convenience function to export analysis as JSON."""
    return JSONExporter(pretty=pretty).export_analysis(report)


def export_optimization_json(result: OptimizationResult, pretty: bool = True) -> str:
    """Convenience function to export optimization as JSON."""
    return JSONExporter(pretty=pretty).export_optimization(result)


def export_validation_json(report: ValidationReport, pretty: bool = True) -> str:
    """Convenience function to export validation as JSON."""
    return JSONExporter(pretty=pretty).export_validation(report)


def export_combined_json(
    analysis: AnalysisReport | None = None,
    optimization: OptimizationResult | None = None,
    validation: ValidationReport | None = None,
    pretty: bool = True,
) -> str:
    """Convenience function to export combined report as JSON."""
    return JSONExporter(pretty=pretty).export_combined(analysis, optimization, validation)