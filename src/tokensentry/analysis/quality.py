"""Quality scoring - clarity, completeness, actionability metrics."""

from __future__ import annotations

import re

from tokensentry.analysis import BaseAnalyzer
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class QualityAnalyzer(BaseAnalyzer):
    """Compute quality scores for prompts."""

    name = "quality"
    description = "Score prompt clarity, completeness, structure, conciseness, and actionability"

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze prompt quality."""
        scores = self._compute_scores(prompt, sections, requirements)

        # Report scores
        findings: list[Finding] = []
        findings.append(Finding(
            code="QUALITY_SCORES",
            severity=Severity.INFO,
            message="Prompt quality scores computed",
            evidence=(
                f"Clarity: {scores['clarity']:.2f}, "
                f"Completeness: {scores['completeness']:.2f}, "
                f"Structure: {scores['structure']:.2f}, "
                f"Conciseness: {scores['conciseness']:.2f}, "
                f"Actionability: {scores['actionability']:.2f}, "
                f"Overall: {scores['overall']:.2f}"
            ),
            suggestion="Scores range 0-1; aim for >0.7 in each dimension",
        ))

        # Flag low scores
        for dimension, score in scores.items():
            if dimension != "overall" and score < 0.4:
                findings.append(Finding(
                    code=f"LOW_{dimension.upper()}",
                    severity=Severity.WARNING,
                    message=f"Low {dimension} score: {score:.2f}",
                    evidence=self._get_dimension_evidence(dimension, prompt, sections, requirements),
                    suggestion=self._get_dimension_suggestion(dimension),
                ))

        return findings

    def _compute_scores(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
    ) -> dict[str, float]:
        """Compute all quality dimensions."""
        prompt_lower = prompt.lower()

        scores = {
            "clarity": self._score_clarity(prompt),
            "completeness": self._score_completeness(prompt_lower, sections, requirements),
            "structure": self._score_structure(sections),
            "conciseness": self._score_conciseness(prompt),
            "actionability": self._score_actionability(prompt_lower, sections),
        }

        # Overall is average
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores

    def _score_clarity(self, prompt: str) -> float:
        """Score based on absence of ambiguous language."""
        # Already detected by AmbiguityAnalyzer, but compute inverse
        ambiguous_patterns = [
            r"\b(some|several|many|a few|a lot|various)\b",
            r"\b(etc|and so on|and more)\b",
            r"\b(probably|maybe|might|could be)\b",
            r"\b(as appropriate|as needed|where applicable)\b",
            r"\b(if possible|if feasible)\b",
        ]

        penalty = 0.0
        for pattern in ambiguous_patterns:
            matches = len(re.findall(pattern, prompt, re.IGNORECASE))
            penalty += matches * 0.05

        return max(0.0, 1.0 - penalty)

    def _score_completeness(
        self,
        prompt_lower: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
    ) -> float:
        """Score based on presence of key prompt components."""
        components = {
            "role": any(w in prompt_lower for w in ["act as", "role", "you are", "as a", "persona"]),
            "context": any(w in prompt_lower for w in ["context", "background", "given", "provided", "assume"]),
            "task": any(w in prompt_lower for w in ["task", "objective", "goal", "create", "write", "generate", "analyze"]),
            "constraints": any(r.type in ("positive", "negative", "value") for r in requirements),
            "output_format": any(r.type in ("format", "output", "schema") for r in requirements),
            "examples": any(s.type == "code_fence" for s in sections),
        }

        return sum(components.values()) / len(components)

    def _score_structure(self, sections: list[PromptSection]) -> float:
        """Score based on structural organization."""
        if not sections:
            return 0.0

        heading_count = sum(1 for s in sections if s.type == "heading")
        has_sections = heading_count > 0

        # Good structure: has headings, balanced sections
        if has_sections and len(sections) >= 3:
            return min(1.0, 0.4 + heading_count * 0.1 + len(sections) * 0.02)
        elif has_sections:
            return 0.5
        else:
            return 0.2

    def _score_conciseness(self, prompt: str) -> float:
        """Score based on token efficiency."""
        words = len(prompt.split())
        if words == 0:
            return 0.0

        # Target: 200-500 words for good conciseness
        if words <= 100:
            return min(1.0, words / 100)
        elif words <= 500:
            return 1.0
        elif words <= 1000:
            return 1.0 - (words - 500) / 1000
        else:
            return max(0.0, 500 / words)

    def _score_actionability(
        self,
        prompt_lower: str,
        sections: list[PromptSection],
    ) -> float:
        """Score based on explicit, actionable instructions."""
        action_verbs = [
            "create", "write", "generate", "analyze", "explain", "list", "describe",
            "compare", "implement", "build", "design", "develop", "produce", "output",
            "return", "provide", "give", "show", "display", "format", "convert",
            "transform", "extract", "parse", "validate", "check", "verify", "ensure",
        ]

        found_verbs = sum(1 for v in action_verbs if v in prompt_lower)

        # Also check for numbered steps
        numbered_steps = len(re.findall(r"^\s*\d+\.\s+\w", prompt_lower, re.MULTILINE))

        score = min(1.0, found_verbs * 0.07 + numbered_steps * 0.1 + 0.1)
        return score

    def _get_dimension_evidence(self, dimension: str, prompt: str, sections: list[PromptSection], requirements: list[Requirement]) -> str:
        """Get evidence for low score."""
        evidence = {
            "clarity": "Contains vague quantifiers, hedging, or underspecified conditions",
            "completeness": "Missing role, context, task, constraints, output format, or examples",
            "structure": "Lacks headings or has too few sections for content size",
            "conciseness": f"Prompt is {'very long' if len(prompt) > 1000 else 'very short'} ({len(prompt.split())} words)",
            "actionability": "Few explicit action verbs or numbered steps",
        }
        return evidence.get(dimension, "Low score detected")

    def _get_dimension_suggestion(self, dimension: str) -> str:
        """Get suggestion for improving dimension."""
        suggestions = {
            "clarity": "Replace vague terms with specific values; remove hedging; define conditions explicitly",
            "completeness": "Add missing components: role, context, clear task, constraints, output format, examples",
            "structure": "Add descriptive headings; organize into logical sections",
            "conciseness": "Remove redundancy; consolidate repeated instructions; use references instead of repetition",
            "actionability": "Use imperative verbs; break into numbered steps; specify exact actions",
        }
        return suggestions.get(dimension, "Review and improve")


# Register
from tokensentry.analysis import registry

registry.register(QualityAnalyzer())