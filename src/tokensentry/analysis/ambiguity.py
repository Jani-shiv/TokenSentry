"""Ambiguity analysis - vague language detection."""

from __future__ import annotations

import re

from tokensentry.analysis import BaseAnalyzer
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class AmbiguityAnalyzer(BaseAnalyzer):
    """Detect ambiguous language in prompts."""

    name = "ambiguity"
    description = "Detect vague quantifiers, open-ended references, and unclear instructions"

    # Ambiguity patterns with descriptions
    PATTERNS = [
        # Vague quantifiers
        (r"\b(some|several|many|a few|a lot|lots of|various|multiple)\b", "vague quantifier",
         "Replace with specific numbers or ranges"),
        (r"\b(a number of|a variety of|a range of)\b", "vague quantifier",
         "Specify exact count or range"),

        # Open-ended references
        (r"\b(etc|and so on|and more|and others|among others)\b", "open-ended list",
         "List all items explicitly or define clear criteria"),
        (r"\b(such as|including|like|e\.g\.)\s+\w+\s*(?:,\s*\w+)*\s*$", "incomplete example list",
         "Complete the example list or add 'for example' context"),

        # Uncertainty hedging
        (r"\b(probably|maybe|might|could be|likely|possibly|potentially)\b", "uncertainty",
         "State requirements definitively or specify conditions"),
        (r"\b(should|ought to|ideally|preferably)\b", "weak obligation",
         "Use 'must' for requirements, 'should' only for preferences"),

        # Conditional without criteria
        (r"\b(as appropriate|as needed|where applicable|when necessary|if needed)\b", "conditional without criteria",
         "Define specific criteria for when this applies"),
        (r"\b(if possible|if feasible|where practical)\b", "conditional without criteria",
         "Specify constraints that determine feasibility"),

        # Vague references
        (r"\b(the above|the following|the previous|mentioned earlier|as stated)\b", "vague reference",
         "Reference specific section numbers or quote the relevant text"),
        (r"\b(here|there|this|that)\s+(?:is|are|was|were)\b", "vague demonstrative",
         "Be explicit about what 'this' refers to"),

        # Time/quantity without units
        (r"\b(short|long|brief|quick|fast|slow|large|small|big|tiny)\b(?!\\s*(?:term|time|period|duration|size|amount))", "relative without scale",
         "Add specific measurements (e.g., 'under 500 tokens', 'within 2 seconds')"),
    ]

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze for ambiguous language."""
        findings: list[Finding] = []

        for pattern, amb_type, suggestion in self.PATTERNS:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"AMBIGUOUS_{amb_type.upper().replace(' ', '_').replace('-', '_')}",
                    severity=Severity.INFO,
                    message=f"Ambiguous language: {amb_type}",
                    evidence=match.group(0),
                    suggestion=suggestion,
                    location=(line_num, line_num),
                ))

        # Check for missing context in requirements
        findings.extend(self._check_requirement_clarity(requirements))

        # Check for underspecified output expectations
        findings.extend(self._check_output_specificity(prompt, requirements))

        return findings

    def _check_requirement_clarity(self, requirements: list[Requirement]) -> list[Finding]:
        """Check if requirements are specific enough."""
        findings: list[Finding] = []

        for req in requirements:
            if req.type in ("positive", "negative") and not req.exact_value:
                # Check for vague action verbs without objects
                vague_verbs = ["handle", "process", "manage", "deal with", "take care of"]
                for verb in vague_verbs:
                    if verb in req.text.lower():
                        findings.append(Finding(
                            code="VAGUE_ACTION_VERB",
                            severity=Severity.INFO,
                            message=f"Vague action verb '{verb}' in requirement",
                            evidence=req.text[:100],
                            suggestion=f"Specify what exactly to {verb} and how",
                            location=req.line_range,
                        ))

        return findings

    def _check_output_specificity(self, prompt: str, requirements: list[Requirement]) -> list[Finding]:
        """Check if output format is sufficiently specified."""
        findings: list[Finding] = []

        has_format_req = any(r.type == "format" for r in requirements)
        has_output_req = any(r.type == "output" for r in requirements)
        has_schema_req = any(r.type == "schema" for r in requirements)

        if not (has_format_req or has_output_req or has_schema_req):
            # Check if prompt implies structured output
            output_indicators = ["return", "output", "generate", "produce", "create", "format as"]
            if any(ind in prompt.lower() for ind in output_indicators):
                findings.append(Finding(
                    code="IMPLICIT_OUTPUT_FORMAT",
                    severity=Severity.INFO,
                    message="Prompt implies structured output but no format specified",
                    evidence="Found output-related verbs without explicit format requirement",
                    suggestion="Add explicit output format requirement (JSON, YAML, Markdown, etc.)",
                ))

        return findings


# Register
from tokensentry.analysis import registry

registry.register(AmbiguityAnalyzer())