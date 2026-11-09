"""Analysis module registry."""

from __future__ import annotations

from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class BaseAnalyzer:
    """Base class for prompt analyzers."""

    name: str = "base"
    description: str = "Base analyzer"

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze prompt and return findings."""
        raise NotImplementedError


class AnalyzerRegistry:
    """Registry for analyzer modules."""

    def __init__(self) -> None:
        self._analyzers: dict[str, BaseAnalyzer] = {}

    def register(self, analyzer: BaseAnalyzer) -> None:
        """Register an analyzer."""
        self._analyzers[analyzer.name] = analyzer

    def get(self, name: str) -> BaseAnalyzer | None:
        """Get analyzer by name."""
        return self._analyzers.get(name)

    def get_all(self) -> list[BaseAnalyzer]:
        """Get all registered analyzers."""
        return list(self._analyzers.values())

    def run_all(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Run all analyzers and collect findings."""
        findings: list[Finding] = []
        for analyzer in self._analyzers.values():
            try:
                findings.extend(
                    analyzer.analyze(
                        prompt, sections, requirements, technical_literals
                    )
                )
            except Exception as e:
                findings.append(
                    Finding(
                        code="ANALYZER_ERROR",
                        severity=Severity.WARNING,
                        message=f"Analyzer '{analyzer.name}' failed: {e}",
                        evidence=str(e),
                    )
                )
        return findings


# Global registry instance
registry = AnalyzerRegistry()