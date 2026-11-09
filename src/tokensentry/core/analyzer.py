"""Prompt analyzer with structure, redundancy, and quality analysis."""

from __future__ import annotations

import re
from collections import Counter

from tokensentry.config import get_config, validate_prompt_content
from tokensentry.models import (
    AnalysisReport,
    Finding,
    PromptSection,
    PromptStats,
    Requirement,
    Severity,
    TechnicalLiteral,
    TokenCountKind,
    TokenizerInfo,
)
from tokensentry.tokenizers.registry import get_tokenizer


def analyze_prompt(
    prompt: str,
    tokenizer_name: str | None = None,
    prompt_id: str | None = None,
) -> AnalysisReport:
    """Analyze a prompt for structure, quality, and token usage.

    Args:
        prompt: The prompt text to analyze
        tokenizer_name: Optional tokenizer name (uses default if not provided)
        prompt_id: Optional identifier for the prompt

    Returns:
        Complete analysis report
    """
    config = get_config()
    validate_prompt_content(prompt, config)

    # Get tokenizer
    if tokenizer_name is None:
        tokenizer_name = config.default_tokenizer
    tokenizer = get_tokenizer(tokenizer_name)

    # Basic stats
    stats = _compute_stats(prompt)

    # Parse sections
    sections = _parse_sections(prompt)

    # Extract requirements
    requirements = _extract_requirements(prompt, sections)

    # Find technical literals
    technical_literals = _find_technical_literals(prompt)

    # Detect findings
    findings = _detect_findings(prompt, sections, requirements, technical_literals)

    # Compute quality scores
    quality_scores = _compute_quality_scores(prompt, sections, findings)

    # Token count
    token_count = tokenizer.count(prompt)

    return AnalysisReport(
        prompt_id=prompt_id or "unknown",
        stats=stats,
        tokenizer=TokenizerInfo(
            name=tokenizer.name,
            version=getattr(tokenizer, "version", None),
            model_id=getattr(tokenizer, "model_id", None),
            encoding=getattr(tokenizer, "encoding", None),
            count_kind=tokenizer.count_kind,
            is_exact=tokenizer.count_kind == TokenCountKind.EXACT,
        ),
        token_count=token_count,
        sections=sections,
        requirements=requirements,
        technical_literals=technical_literals,
        findings=findings,
        quality_scores=quality_scores,
    )


def _compute_stats(prompt: str) -> PromptStats:
    lines = prompt.splitlines()
    non_empty = [line for line in lines if line.strip()]
    words = len(prompt.split())

    return PromptStats(
        characters=len(prompt),
        words=words,
        lines=len(lines),
        non_empty_lines=len(non_empty),
        avg_line_length=sum(len(line) for line in lines) / len(lines) if lines else 0.0,
        max_line_length=max((len(line) for line in lines), default=0),
    )


def _parse_sections(prompt: str) -> list[PromptSection]:
    """Parse prompt into logical sections."""
    sections: list[PromptSection] = []
    lines = prompt.splitlines()
    current_section: PromptSection | None = None
    in_code_fence = False
    code_fence_lang = None

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
    code_fence_pattern = re.compile(r"^```(\w*)\s*$")
    list_pattern = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.+)$")

    for i, line in enumerate(lines):
        line_num = i + 1

        # Handle code fences
        code_fence_match = code_fence_pattern.match(line)
        if code_fence_match:
            if not in_code_fence:
                # Starting code fence
                if current_section:
                    current_section.end_line = line_num - 1
                    sections.append(current_section)
                in_code_fence = True
                code_fence_lang = code_fence_match.group(1) or None
                current_section = PromptSection(
                    type="code_fence",
                    content=line + "\n",
                    start_line=line_num,
                    end_line=line_num,
                    language=code_fence_lang,
                )
            else:
                # Ending code fence
                in_code_fence = False
                current_section.content += line + "\n"
                current_section.end_line = line_num
                sections.append(current_section)
                current_section = None
                code_fence_lang = None
            continue

        if in_code_fence and current_section is not None:
            current_section.content += line + "\n"
            current_section.end_line = line_num
            continue

        # Handle headings
        heading_match = heading_pattern.match(line)
        if heading_match:
            if current_section:
                current_section.end_line = line_num - 1
                sections.append(current_section)
            level = len(heading_match.group(1))
            current_section = PromptSection(
                type="heading",
                title=heading_match.group(2).strip(),
                content=line + "\n",
                start_line=line_num,
                end_line=line_num,
                level=level,
            )
            continue

        # Handle lists
        list_match = list_pattern.match(line)
        if list_match:
            if current_section and current_section.type != "list":
                current_section.end_line = line_num - 1
                sections.append(current_section)
            if not current_section or current_section.type != "list":
                current_section = PromptSection(
                    type="list",
                    content=line + "\n",
                    start_line=line_num,
                    end_line=line_num,
                )
            else:
                current_section.content += line + "\n"
                current_section.end_line = line_num
            continue

        # Regular paragraph content
        if line.strip():
            if not current_section:
                current_section = PromptSection(
                    type="paragraph",
                    content=line + "\n",
                    start_line=line_num,
                    end_line=line_num,
                )
            elif current_section.type == "paragraph":
                current_section.content += line + "\n"
                current_section.end_line = line_num
            else:
                # Different section type, start new paragraph
                current_section.end_line = line_num - 1
                sections.append(current_section)
                current_section = PromptSection(
                    type="paragraph",
                    content=line + "\n",
                    start_line=line_num,
                    end_line=line_num,
                )
        else:
            # Empty line - end current section if it's a paragraph
            if current_section and current_section.type == "paragraph":
                current_section.end_line = line_num - 1
                sections.append(current_section)
                current_section = None

    # Don't forget the last section
    if current_section:
        sections.append(current_section)

    return sections


def _extract_requirements(prompt: str, sections: list[PromptSection]) -> list[Requirement]:
    """Extract explicit requirements and constraints."""
    requirements: list[Requirement] = []
    lines = prompt.splitlines()

    # Patterns for different requirement types
    patterns = [
        # Must/should statements
        (r"\b(must|shall|required to|have to)\b", "positive"),
        (r"\b(must not|shall not|never|do not|don't|prohibited|forbidden)\b", "negative"),
        # Value constraints
        (
            r"\b(maximum|minimum|at most|at least|exactly|no more than|no less than)\s+(\d+)",
            "value",
        ),
        # Format requirements
        (r"\b(json|yaml|xml|csv|markdown|html)\b", "format"),
        # Output format
        (r"\b(output|return|respond|format|structure)\s+(as|in|with)\b", "output"),
        # Schema references
        (r"\b(schema|specification|contract|interface)\b", "schema"),
    ]

    value_constraint = patterns[2]
    patterns[2] = (value_constraint[0], value_constraint[1])  # type: ignore[assignment]

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower:
            continue

        for pattern, req_type in patterns:
            for _match in re.finditer(pattern, line_lower, re.IGNORECASE):
                # Find which section this line belongs to
                source_section = None
                for section in sections:
                    if section.start_line <= i + 1 <= section.end_line:
                        source_section = section.type
                        if section.title:
                            source_section = f"{section.type}:{section.title}"
                        break

                req = Requirement(
                    text=line.strip(),
                    type=req_type,  # type: ignore[arg-type]
                    source_section=source_section,
                    line_range=(i + 1, i + 1),
                    is_critical=req_type in ("negative", "value"),
                )

                # Extract exact value for value constraints
                if req_type == "value":
                    value_match = re.search(r"(\d+)", line)
                    if value_match:
                        req.exact_value = value_match.group(1)

                requirements.append(req)

    # Deduplicate similar requirements
    seen: set[str] = set()
    unique: list[Requirement] = []
    for req in requirements:
        key = f"{req.type}:{req.text[:100]}"
        if key not in seen:
            seen.add(key)
            unique.append(req)

    return unique


def _find_technical_literals(prompt: str) -> list[TechnicalLiteral]:
    """Find technical literals that must be preserved."""
    literals: list[TechnicalLiteral] = []
    lines = prompt.splitlines()

    patterns = [
        # Code blocks (already handled by sections, but catch inline)
        (r"`([^`\n]{3,})`", "code"),
        # Commands
        (
            r"\b(?:kubectl|docker|git|npm|pip|python|node|curl|wget|ssh|scp|rsync|terraform|ansible|helm|kubectl)\S*",
            "command",
        ),
        # URLs
        (r"https?://[^\s\"'<>\)]+", "url"),
        # File paths
        (r"(?:[~/]|\.\./|\./)[\w\-./]+", "file_path"),
        # JSON-like
        (r"\{[^{}]*\}", "json"),
        # YAML-like keys
        (r"^\s*[\w\-]+:\s*\S+", "yaml"),
        # Environment variables
        (r"\$\{?[A-Z_][A-Z0-9_]*\}?", "variable"),
        # Kubernetes resources
        (r"\b(apiVersion|kind|metadata|spec|template|selector)\b", "yaml"),
        # Version numbers
        (r"\bv?\d+\.\d+\.\d+(?:-[\w.]+)?\b", "constant"),
    ]

    for i, line in enumerate(lines):
        for pattern, lit_type in patterns:
            for match in re.finditer(pattern, line):
                value = match.group(0)
                # Skip very short matches
                if len(value) < 3:
                    continue

                # Determine context (surrounding lines)
                context_start = max(0, i - 1)
                context_end = min(len(lines), i + 2)
                context = "\n".join(lines[context_start:context_end])

                priority = 10
                if lit_type in ("command", "url", "file_path", "json", "yaml"):
                    priority = 10
                elif lit_type in ("variable", "constant"):
                    priority = 8
                else:
                    priority = 6

                literals.append(
                    TechnicalLiteral(
                        type=lit_type,  # type: ignore[arg-type]
                        value=value,
                        context=context,
                        line_range=(i + 1, i + 1),
                        preservation_priority=priority,
                    )
                )

    # Deduplicate
    seen: set[str] = set()
    unique: list[TechnicalLiteral] = []
    for lit in literals:
        key = f"{lit.type}:{lit.value}"
        if key not in seen:
            seen.add(key)
            unique.append(lit)

    return unique


def _detect_findings(
    prompt: str,
    sections: list[PromptSection],
    requirements: list[Requirement],
    technical_literals: list[TechnicalLiteral],
) -> list[Finding]:
    """Detect issues and patterns in the prompt."""
    findings: list[Finding] = []
    lines = prompt.splitlines()

    # 1. Repeated lines
    non_empty = [line.strip() for line in lines if line.strip()]
    repeated = [line for line, count in Counter(non_empty).items() if count > 1]
    for line in repeated:
        findings.append(
            Finding(
                code="REPEATED_LINE",
                severity=Severity.INFO,
                message="An identical non-empty line appears more than once.",
                evidence=line[:160],
                suggestion="Consider consolidating duplicate instructions.",
            )
        )

    # 2. Empty prompt
    if not prompt.strip():
        findings.append(
            Finding(
                code="EMPTY_PROMPT",
                severity=Severity.WARNING,
                message="The prompt is empty or whitespace only.",
                suggestion="Provide a prompt with instructions or context.",
            )
        )

    # 3. Very long lines
    for i, line in enumerate(lines):
        if len(line) > 500:
            findings.append(
                Finding(
                    code="LONG_LINE",
                    severity=Severity.INFO,
                    message=f"Line {i + 1} exceeds 500 characters.",
                    evidence=line[:100] + "..." if len(line) > 100 else line,
                    suggestion="Consider breaking long lines for readability.",
                )
            )

    # 4. Repeated phrases (3+ words)
    words = prompt.lower().split()
    if len(words) >= 6:
        trigrams = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
        repeated_trigrams = [t for t, c in Counter(trigrams).items() if c > 2]
        for trigram in repeated_trigrams[:5]:  # Limit to top 5
            findings.append(
                Finding(
                    code="REPEATED_PHRASE",
                    severity=Severity.INFO,
                    message=f"Three-word phrase repeated multiple times: '{trigram}'",
                    evidence=trigram,
                    suggestion="Consider consolidating repetitive language.",
                )
            )

    # 5. Ambiguous language
    ambiguous_patterns = [
        (r"\b(some|several|many|a few|a lot|various)\b", "vague quantifier"),
        (r"\b(etc|and so on|and more)\b", "open-ended list"),
        (r"\b(probably|maybe|might|could be|likely)\b", "uncertainty"),
        (r"\b(as appropriate|as needed|where applicable)\b", "conditional without criteria"),
    ]
    for pattern, desc in ambiguous_patterns:
        for match in re.finditer(pattern, prompt, re.IGNORECASE):
            line_num = prompt[: match.start()].count("\n") + 1
            findings.append(
                Finding(
                    code="AMBIGUOUS_LANGUAGE",
                    severity=Severity.INFO,
                    message=f"Ambiguous language detected: {desc}",
                    evidence=match.group(0),
                    location=(line_num, line_num),
                    suggestion="Replace with specific criteria or explicit values.",
                )
            )

    # 6. Potential contradictions (simple heuristic)
    positive_reqs = [r for r in requirements if r.type == "positive"]
    negative_reqs = [r for r in requirements if r.type == "negative"]
    for pos in positive_reqs:
        for neg in negative_reqs:
            pos_words = set(pos.text.lower().split())
            neg_words = set(neg.text.lower().split())
            # Check for direct opposition
            if len(pos_words & neg_words) > 2:
                findings.append(
                    Finding(
                        code="POTENTIAL_CONTRADICTION",
                        severity=Severity.WARNING,
                        message=(
                            "Potential contradiction between "
                            "positive and negative requirements."
                        ),
                        evidence=f"Positive: {pos.text[:80]} | Negative: {neg.text[:80]}",
                        suggestion="Review conflicting requirements for consistency.",
                    )
                )

    # 7. Missing output format specification
    has_output_format = any(r.type in ("format", "output", "schema") for r in requirements)
    if not has_output_format and len(prompt) > 200:
        findings.append(
            Finding(
                code="MISSING_OUTPUT_FORMAT",
                severity=Severity.INFO,
                message="No explicit output format specified for a substantial prompt.",
                suggestion="Consider adding output format requirements (JSON, YAML, etc.).",
            )
        )

    # 8. Security-related patterns
    if get_config().enable_security_checks:
        security_patterns = [
            (r"(?i)(api[_-]?key|secret|password|token|credential)\s*[:=]\s*\S+", "exposed secret"),
            (r"(?i)ignore\s+(?:previous|above|all)\s+instructions", "prompt injection"),
            (r"(?i)(?:system|admin|root)\s*[:=]\s*true", "privilege escalation"),
            (r"(?i)execute\s+(?:command|code|script)", "command execution"),
        ]
        for pattern, desc in security_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[: match.start()].count("\n") + 1
                findings.append(
                    Finding(
                        code="SECURITY_RISK",
                        severity=Severity.WARNING,
                        message=f"Potential security risk: {desc}",
                        evidence=match.group(0)[:100],
                        location=(line_num, line_num),
                        suggestion="Review and remove sensitive data or unsafe instructions.",
                    )
                )

    return findings


def _compute_quality_scores(
    prompt: str,
    sections: list[PromptSection],
    findings: list[Finding],
) -> dict[str, float]:
    """Compute quality scores for the prompt."""
    scores: dict[str, float] = {}

    # Clarity: inverse of ambiguity findings
    ambiguity_count = sum(1 for f in findings if f.code == "AMBIGUOUS_LANGUAGE")
    scores["clarity"] = max(0.0, 1.0 - (ambiguity_count * 0.1))

    # Completeness: has role, context, constraints, output format
    completeness = 0.0
    prompt_lower = prompt.lower()
    if any(w in prompt_lower for w in ["act as", "role", "you are", "as a"]):
        completeness += 0.25
    if any(w in prompt_lower for w in ["context", "background", "given", "provided"]):
        completeness += 0.25
    if any(f.code in ("MISSING_OUTPUT_FORMAT",) for f in findings):
        completeness += 0.0
    else:
        completeness += 0.25
    if any(r.type in ("positive", "negative", "value") for r in []):  # requirements would be passed
        completeness += 0.25
    scores["completeness"] = min(1.0, completeness)

    # Structure: has headings, sections
    heading_count = sum(1 for s in sections if s.type == "heading")
    scores["structure"] = min(1.0, heading_count * 0.2 + 0.2)

    # Conciseness: inverse of token density
    words = len(prompt.split())
    if words > 0:
        scores["conciseness"] = min(1.0, 500 / words)
    else:
        scores["conciseness"] = 0.0

    # Actionability: has explicit instructions
    action_verbs = [
        "create", "write", "generate", "analyze", "explain",
        "list", "describe", "compare", "implement",
    ]
    action_count = sum(1 for v in action_verbs if v in prompt_lower)
    scores["actionability"] = min(1.0, action_count * 0.15 + 0.1)

    # Overall
    scores["overall"] = sum(scores.values()) / len(scores) if scores else 0.0

    return scores