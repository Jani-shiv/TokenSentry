"""Prompt analyzer with modular analysis engines."""

from __future__ import annotations

import re

from tokensentry.analysis import registry as analysis_registry
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

    # Run all modular analyzers
    findings = analysis_registry.run_all(prompt, sections, requirements, technical_literals)

    # Add basic findings (empty prompt, etc.)
    if not prompt.strip():
        findings.append(Finding(
            code="EMPTY_PROMPT",
            severity=Severity.WARNING,
            message="The prompt is empty or whitespace only.",
            suggestion="Provide a prompt with instructions or context.",
        ))

    # Compute quality scores from QualityAnalyzer findings
    quality_scores = _extract_quality_scores(findings)

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
    """Compute basic prompt statistics."""
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
    table_pattern = re.compile(r"^\|.*\|$")

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

        if in_code_fence and current_section:
            current_section.content += line + "\n"
            current_section.end_line = line_num
            continue

        # Handle tables
        if table_pattern.match(line):
            if current_section and current_section.type != "table":
                current_section.end_line = line_num - 1
                sections.append(current_section)
            if not current_section or current_section.type != "table":
                current_section = PromptSection(
                    type="table",
                    content=line + "\n",
                    start_line=line_num,
                    end_line=line_num,
                )
            else:
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

    import re

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


def _extract_quality_scores(findings: list[Finding]) -> dict[str, float]:
    """Extract quality scores from QualityAnalyzer findings."""
    scores = {}
    for finding in findings:
        if finding.code == "QUALITY_SCORES":
            # Parse evidence string for scores
            evidence = finding.evidence or ""
            for part in evidence.split(", "):
                if ": " in part:
                    key, val = part.split(": ", 1)
                    try:
                        scores[key.lower()] = float(val)
                    except ValueError:
                        pass
    return scores