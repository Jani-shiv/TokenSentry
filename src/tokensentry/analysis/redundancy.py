"""Redundancy analysis - duplicate detection."""

from __future__ import annotations

from collections import Counter

from tokensentry.analysis import BaseAnalyzer
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class RedundancyAnalyzer(BaseAnalyzer):
    """Detect redundant content in prompts."""

    name = "redundancy"
    description = "Detect duplicate lines, phrases, and semantic repetition"

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze for redundancy."""
        findings: list[Finding] = []

        lines = prompt.splitlines()

        # 1. Exact duplicate non-empty lines
        findings.extend(self._find_exact_duplicate_lines(lines))

        # 2. Repeated phrases (n-grams)
        findings.extend(self._find_repeated_phrases(prompt))

        # 3. Duplicate requirements
        findings.extend(self._find_duplicate_requirements(requirements))

        # 4. Repeated technical literals
        findings.extend(self._find_repeated_literals(technical_literals))

        # 5. Semantic similarity in adjacent sections
        findings.extend(self._find_semantic_repetition(sections))

        return findings

    def _find_exact_duplicate_lines(self, lines: list[str]) -> list[Finding]:
        """Find exact duplicate non-empty lines."""
        findings: list[Finding] = []
        non_empty = [(i + 1, line.strip()) for i, line in enumerate(lines) if line.strip()]
        counter = Counter(text for _, text in non_empty)

        for text, count in counter.items():
            if count > 1:
                line_nums = [str(ln) for ln, txt in non_empty if txt == text]
                findings.append(Finding(
                    code="DUPLICATE_LINE",
                    severity=Severity.INFO,
                    message=f"Identical line appears {count} times",
                    evidence=text[:160],
                    suggestion="Consider consolidating duplicate instructions",
                    location=(int(line_nums[0]), int(line_nums[-1])),
                ))
        return findings

    def _find_repeated_phrases(self, prompt: str) -> list[Finding]:
        """Find repeated n-gram phrases."""
        findings: list[Finding] = []
        words = prompt.lower().split()

        if len(words) < 6:
            return findings

        # Trigrams (3-word phrases)
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
        trigram_counts = Counter(trigrams)

        for phrase, count in trigram_counts.most_common(10):
            if count > 2 and len(phrase) > 10:
                findings.append(Finding(
                    code="REPEATED_PHRASE",
                    severity=Severity.INFO,
                    message=f"Three-word phrase repeated {count} times",
                    evidence=phrase,
                    suggestion="Consider consolidating repetitive language",
                ))

        # 4-grams for longer patterns
        fourgrams = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]
        fourgram_counts = Counter(fourgrams)

        for phrase, count in fourgram_counts.most_common(5):
            if count > 2 and len(phrase) > 15:
                findings.append(Finding(
                    code="REPEATED_LONG_PHRASE",
                    severity=Severity.INFO,
                    message=f"Four-word phrase repeated {count} times",
                    evidence=phrase,
                    suggestion="Consider extracting repeated pattern into a reference",
                ))

        return findings

    def _find_duplicate_requirements(self, requirements: list[Requirement]) -> list[Finding]:
        """Find semantically duplicate requirements."""
        findings: list[Finding] = []

        if len(requirements) < 2:
            return findings

        # Group by type and compare text similarity
        by_type: dict[str, list[Requirement]] = {}
        for req in requirements:
            by_type.setdefault(req.type, []).append(req)

        for req_type, reqs in by_type.items():
            for i, req1 in enumerate(reqs):
                for req2 in reqs[i+1:]:
                    similarity = self._text_similarity(req1.text, req2.text)
                    if similarity > 0.8:
                        findings.append(Finding(
                            code="DUPLICATE_REQUIREMENT",
                            severity=Severity.INFO,
                            message=f"Similar {req_type} requirements detected",
                            evidence=f"Req 1: {req1.text[:80]} | Req 2: {req2.text[:80]}",
                            suggestion="Consider consolidating into single requirement",
                            location=req1.line_range,
                        ))

        return findings

    def _find_repeated_literals(self, technical_literals: list[TechnicalLiteral]) -> list[Finding]:
        """Find repeated technical literals."""
        findings: list[Finding] = []

        counter = Counter(lit.value for lit in technical_literals)
        for value, count in counter.items():
            if count > 1:
                findings.append(Finding(
                    code="REPEATED_LITERAL",
                    severity=Severity.INFO,
                    message=f"Technical literal appears {count} times",
                    evidence=value[:100],
                    suggestion="Consider defining once and referencing",
                ))

        return findings

    def _find_semantic_repetition(self, sections: list[PromptSection]) -> list[Finding]:
        """Find semantically similar adjacent sections."""
        findings: list[Finding] = []

        for i in range(len(sections) - 1):
            s1, s2 = sections[i], sections[i + 1]
            if s1.type == s2.type == "paragraph":
                similarity = self._text_similarity(s1.content, s2.content)
                if similarity > 0.7:
                    findings.append(Finding(
                        code="SIMILAR_ADJACENT_SECTIONS",
                        severity=Severity.INFO,
                        message="Adjacent sections have very similar content",
                        evidence=f"Section {i+1}: {s1.content[:80]} | Section {i+2}: {s2.content[:80]}",
                        suggestion="Consider merging similar sections",
                        location=(s1.start_line, s2.end_line),
                    ))

        return findings

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple Jaccard similarity on word sets."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)


# Register
from tokensentry.analysis import registry

registry.register(RedundancyAnalyzer())