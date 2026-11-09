"""Optimization profiles and transformation primitives."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from tokensentry.config import get_config, validate_prompt_content
from tokensentry.models import (
    OptimizationProfile,
    OptimizationResult,
    Severity,
    TechnicalLiteral,
    TokenizerInfo,
    Transformation,
)
from tokensentry.tokenizers.registry import get_tokenizer


@dataclass
class _OptimizationContext:
    """Internal optimization context."""

    original: str
    lines: list[str]
    technical_literals: list[TechnicalLiteral]
    tokenizer: Any
    profile: OptimizationProfile
    transformations: list[Transformation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Transformation function type
TransformFunc = Callable[[_OptimizationContext], None]


# Profile definitions with their transformations
PROFILE_TRANSFORMS: dict[OptimizationProfile, list[TransformFunc]] = {
    OptimizationProfile.CONSERVATIVE: [],
    OptimizationProfile.BALANCED: [],
    OptimizationProfile.AGGRESSIVE: [],
}


def register_transform(profile: OptimizationProfile, func: TransformFunc) -> None:
    """Register a transformation for a profile."""
    PROFILE_TRANSFORMS[profile].append(func)


def optimize_prompt(
    prompt: str,
    profile: OptimizationProfile = OptimizationProfile.CONSERVATIVE,
    tokenizer_name: str | None = None,
    technical_literals: list[TechnicalLiteral] | None = None,
    custom_transforms: list[TransformFunc] | None = None,
) -> OptimizationResult:
    """Optimize a prompt with the specified profile.

    Args:
        prompt: Original prompt text
        profile: Optimization aggressiveness
        tokenizer_name: Tokenizer to use for counting
        technical_literals: Pre-identified technical literals to preserve
        custom_transforms: Optional custom transformations to apply

    Returns:
        Optimization result with transformations and metadata
    """
    config = get_config()
    validate_prompt_content(prompt, config)

    if tokenizer_name is None:
        tokenizer_name = config.default_tokenizer
    tokenizer = get_tokenizer(tokenizer_name)

    # Identify technical literals if not provided
    if technical_literals is None:
        technical_literals = _find_technical_literals(prompt)

    # Create context
    ctx = _OptimizationContext(
        original=prompt,
        lines=prompt.splitlines(),
        technical_literals=technical_literals,
        tokenizer=tokenizer,
        profile=profile,
    )

    # Apply profile-specific optimizations
    for transform in PROFILE_TRANSFORMS[profile]:
        transform(ctx)

    # Apply custom transforms if provided
    if custom_transforms:
        for transform in custom_transforms:
            transform(ctx)

    # Rebuild optimized prompt
    optimized = "\n".join(ctx.lines)

    # Count tokens
    original_tokens = tokenizer.count(prompt)
    optimized_tokens = tokenizer.count(optimized)

    # Calculate token delta for each transformation
    _calculate_token_deltas(ctx, prompt, tokenizer)

    return OptimizationResult(
        original=prompt,
        optimized=optimized,
        profile=profile,
        tokenizer=TokenizerInfo(
            name=tokenizer.name,
            version=getattr(tokenizer, "version", None),
            model_id=getattr(tokenizer, "model_id", None),
            encoding=getattr(tokenizer, "encoding", None),
            count_kind=tokenizer.count_kind,
            is_exact=tokenizer.count_kind.value == "exact",
        ),
        original_token_count=original_tokens,
        optimized_token_count=optimized_tokens,
        token_delta=original_tokens - optimized_tokens,
        transformations=ctx.transformations,
        warnings=ctx.warnings,
        preserved_literals=technical_literals,
    )


def _calculate_token_deltas(
    ctx: _OptimizationContext, original: str, tokenizer: Any
) -> None:
    """Calculate token delta for each transformation by replaying."""
    for t in ctx.transformations:
        # We can't easily replay, so estimate from the original/optimized in transform
        if t.original and t.optimized:
            orig_tokens = tokenizer.count(t.original)
            opt_tokens = tokenizer.count(t.optimized)
            t.token_delta = orig_tokens - opt_tokens


def _find_technical_literals(prompt: str) -> list[TechnicalLiteral]:
    """Find technical literals (simplified version for optimizer)."""
    literals: list[TechnicalLiteral] = []
    lines = prompt.splitlines()

    patterns = [
        (r"`([^`\n]{3,})`", "code"),
        (
            r"\b(?:kubectl|docker|git|npm|pip|python|node|curl|wget|ssh|scp|rsync|terraform|ansible|helm)\S*",
            "command",
        ),
        (r"https?://[^\s\"'<>\)]+", "url"),
        (r"(?:[~/]|\.\./|\./)[\w\-./]+", "file_path"),
        (r"\{[^{}]*\}", "json"),
        (r"^\s*[\w\-]+:\s*\S+", "yaml"),
        (r"\$\{?[A-Z_][A-Z0-9_]*\}?", "variable"),
    ]

    for i, line in enumerate(lines):
        for pattern, lit_type in patterns:
            for match in re.finditer(pattern, line):
                value = match.group(0)
                if len(value) < 3:
                    continue
                literals.append(
                    TechnicalLiteral(
                        type=lit_type,  # type: ignore[arg-type]
                        value=value,
                        line_range=(i + 1, i + 1),
                        preservation_priority=(
                            10
                            if lit_type in ("command", "url", "file_path", "json", "yaml")
                            else 6
                        ),
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


def _is_protected(line: str, technical_literals: list[TechnicalLiteral], line_num: int) -> bool:
    """Check if a line contains protected technical literals."""
    for lit in technical_literals:
        if lit.line_range and lit.line_range[0] <= line_num <= lit.line_range[1]:
            if lit.value in line:
                return True
    return False


# ============================================================================
# CONSERVATIVE TRANSFORMATIONS
# ============================================================================

def _trim_trailing_whitespace(ctx: _OptimizationContext) -> None:
    """Trim trailing whitespace from each line."""
    original_lines = ctx.lines[:]
    ctx.lines = [line.rstrip() for line in ctx.lines]
    if ctx.lines != original_lines:
        ctx.transformations.append(
            Transformation(
                type="trim_trailing_whitespace",
                description="Trimmed trailing whitespace from all lines",
                original="\n".join(original_lines),
                optimized="\n".join(ctx.lines),
                token_delta=0,
            )
        )


def _collapse_blank_lines(ctx: _OptimizationContext) -> None:
    """Collapse multiple consecutive blank lines to single blank line."""
    original_lines = ctx.lines[:]
    compact: list[str] = []
    blank_seen = False
    for line in ctx.lines:
        blank = not line.strip()
        if blank and blank_seen:
            continue
        compact.append(line)
        blank_seen = blank
    ctx.lines = compact
    if ctx.lines != original_lines:
        ctx.transformations.append(
            Transformation(
                type="collapse_blank_lines",
                description="Collapsed multiple consecutive blank lines to single blank line",
                original="\n".join(original_lines),
                optimized="\n".join(ctx.lines),
                token_delta=0,
            )
        )


def _remove_exact_duplicates(ctx: _OptimizationContext) -> None:
    """Remove exact duplicate non-empty lines (preserving first occurrence)."""
    original_lines = ctx.lines[:]
    seen: set[str] = set()
    deduped: list[str] = []
    for line in ctx.lines:
        stripped = line.strip()
        if stripped and stripped in seen:
            continue
        deduped.append(line)
        if stripped:
            seen.add(stripped)
    ctx.lines = deduped
    if ctx.lines != original_lines:
        ctx.transformations.append(
            Transformation(
                type="remove_exact_duplicates",
                description="Removed exact duplicate non-empty lines",
                original="\n".join(original_lines),
                optimized="\n".join(ctx.lines),
                token_delta=0,
            )
        )


def _trim_outer_blank_lines(ctx: _OptimizationContext) -> None:
    """Trim leading/trailing blank lines."""
    original_lines = ctx.lines[:]
    while ctx.lines and not ctx.lines[0].strip():
        ctx.lines.pop(0)
    while ctx.lines and not ctx.lines[-1].strip():
        ctx.lines.pop()
    if ctx.lines != original_lines:
        ctx.transformations.append(
            Transformation(
                type="trim_outer_blank_lines",
                description="Trimmed leading and trailing blank lines",
                original="\n".join(original_lines),
                optimized="\n".join(ctx.lines),
                token_delta=0,
            )
        )


# ============================================================================
# BALANCED TRANSFORMATIONS
# ============================================================================

def _consolidate_repeated_phrases(ctx: _OptimizationContext) -> None:
    """Consolidate repeated phrases within sentences."""
    original = "\n".join(ctx.lines)
    consolidated = _consolidate_phrases_text(original)
    if consolidated != original:
        ctx.lines = consolidated.splitlines()
        ctx.transformations.append(
            Transformation(
                type="consolidate_phrases",
                description="Consolidated repeated phrases within sentences",
                original=original,
                optimized=consolidated,
                token_delta=0,
            )
        )


def _consolidate_phrases_text(text: str) -> str:
    """Consolidate repeated phrases within sentences."""
    lines = text.splitlines()
    result = []
    for line in lines:
        # Replace "X and X and X" patterns
        pattern1 = r"\b(\w+(?:\s+\w+)?)\s+and\s+\1\s+and\s+\1\b"
        line = re.sub(pattern1, r"\1", line, flags=re.IGNORECASE)
        pattern2 = r"\b(\w+(?:\s+\w+)?)\s+and\s+\1\b"
        line = re.sub(pattern2, r"\1", line, flags=re.IGNORECASE)
        # Replace "X, X, X" patterns
        pattern3 = r"\b(\w+(?:\s+\w+)?),\s+\1,\s+\1\b"
        line = re.sub(pattern3, r"\1", line, flags=re.IGNORECASE)
        result.append(line)
    return "\n".join(result)


def _remove_redundant_transitions(ctx: _OptimizationContext) -> None:
    """Remove redundant transition words."""
    original = "\n".join(ctx.lines)
    trimmed = _remove_transitions_text(original)
    if trimmed != original:
        ctx.lines = trimmed.splitlines()
        ctx.transformations.append(
            Transformation(
                type="remove_redundant_transitions",
                description="Removed redundant transition words and fillers",
                original=original,
                optimized=trimmed,
                token_delta=0,
            )
        )


def _remove_transitions_text(text: str) -> str:
    """Remove redundant transition words."""
    transitions = [
        r"\b(in addition|furthermore|moreover|additionally|also|besides)\b",
        r"\b(however|nevertheless|nonetheless|on the other hand)\b",
        r"\b(therefore|thus|consequently|hence|accordingly)\b",
        r"\b(for example|for instance|such as|including)\b",
        r"\b(in conclusion|to summarize|in summary|finally)\b",
    ]

    lines = text.splitlines()
    result = []
    for line in lines:
        original_line = line
        for pattern in transitions:
            # Only remove if the transition appears at the start of a clause
            line = re.sub(f"^{pattern}[,\\s]+", "", line, flags=re.IGNORECASE)
            line = re.sub(f"[;,]\\s*{pattern}[,\\s]+", "; ", line, flags=re.IGNORECASE)
        if line != original_line:
            result.append(line)
        else:
            result.append(line)
    return "\n".join(result)


def _normalize_bullets(ctx: _OptimizationContext) -> None:
    """Normalize bullet point style to consistent format."""
    original = "\n".join(ctx.lines)
    normalized = _normalize_bullets_text(original)
    if normalized != original:
        ctx.lines = normalized.splitlines()
        ctx.transformations.append(
            Transformation(
                type="normalize_bullets",
                description="Normalized bullet point style",
                original=original,
                optimized=normalized,
                token_delta=0,
            )
        )


def _normalize_bullets_text(text: str) -> str:
    """Normalize bullet point style to consistent format."""
    lines = text.splitlines()
    result = []
    for line in lines:
        # Convert various bullet styles to "- "
        line = re.sub(r"^\s*[\*\u2022\u25cf\u25cb\u25a0]\s+", "- ", line)
        line = re.sub(r"^\s*\d+\.\s+", "- ", line)
        result.append(line)
    return "\n".join(result)


def _consolidate_similar_instructions(ctx: _OptimizationContext) -> None:
    """Consolidate adjacent similar instructions."""
    original = "\n".join(ctx.lines)
    consolidated = _consolidate_instructions_text(original, ctx.technical_literals)
    if consolidated != original:
        ctx.lines = consolidated.splitlines()
        ctx.transformations.append(
            Transformation(
                type="consolidate_instructions",
                description="Consolidated adjacent similar instructions",
                original=original,
                optimized=consolidated,
                token_delta=0,
            )
        )


def _consolidate_instructions_text(
    text: str, technical_literals: list[TechnicalLiteral]
) -> str:
    """Consolidate adjacent similar instructions."""
    lines = text.splitlines()
    if len(lines) < 2:
        return text

    result = []
    i = 0
    while i < len(lines):
        current = lines[i]
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            # Simple similarity: same starting verb
            current_words = current.strip().split()
            next_words = next_line.strip().split()
            if current_words and next_words:
                if current_words[0].lower() == next_words[0].lower() and len(current_words) > 2:
                    # Check if not protected
                    if not any(
                        lit.value in current or lit.value in next_line
                        for lit in technical_literals
                    ):
                        # Merge: keep the more complete one
                        if len(next_line) > len(current):
                            result.append(next_line)
                        else:
                            result.append(current)
                        i += 2
                        continue
        result.append(current)
        i += 1

    return "\n".join(result)


# ============================================================================
# AGGRESSIVE TRANSFORMATIONS
# ============================================================================

def _remove_filler_sentences(ctx: _OptimizationContext) -> None:
    """Remove low-value filler sentences."""
    original = "\n".join(ctx.lines)
    compressed = _remove_filler_text(original, ctx.technical_literals)
    if compressed != original:
        ctx.lines = compressed.splitlines()
        ctx.transformations.append(
            Transformation(
                type="remove_filler",
                description="Removed low-value filler sentences",
                original=original,
                optimized=compressed,
                token_delta=0,
                risk_level=Severity.WARNING,
            )
        )
        ctx.warnings.append("Aggressive mode removed sentences deemed low-value. Review carefully.")


def _remove_filler_text(
    text: str, technical_literals: list[TechnicalLiteral]
) -> str:
    """Remove low-value filler sentences."""
    filler_patterns = [
        r"^\s*Please\s+(?:note|be aware|remember|understand)\s+that\s+",
        r"^\s*It\s+is\s+important\s+to\s+(?:note|remember|understand)\s+that\s+",
        r"^\s*I\s+(?:want|would like|need)\s+you\s+to\s+",
        r"^\s*Your\s+task\s+is\s+to\s+",
        r"^\s*Here\s+(?:is|are)\s+(?:the|some)\s+",
    ]

    lines = text.splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue

        # Check if line is mostly filler
        is_filler = False
        for pattern in filler_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                # Check if line has technical content
                has_technical = any(lit.value in line for lit in technical_literals)
                if not has_technical and len(stripped) < 200:
                    is_filler = True
                    break

        if not is_filler:
            result.append(line)

    return "\n".join(result)


def _compress_explanations(ctx: _OptimizationContext) -> None:
    """Compress verbose explanations."""
    original = "\n".join(ctx.lines)
    compressed = _compress_explanations_text(original, ctx.technical_literals)
    if compressed != original:
        ctx.lines = compressed.splitlines()
        ctx.transformations.append(
            Transformation(
                type="compress_explanations",
                description="Compressed verbose explanations",
                original=original,
                optimized=compressed,
                token_delta=0,
                risk_level=Severity.WARNING,
            )
        )


def _compress_explanations_text(
    text: str, technical_literals: list[TechnicalLiteral]
) -> str:
    """Compress verbose explanations."""
    lines = text.splitlines()
    result = []

    for line in lines:
        # Skip if protected
        if any(lit.value in line for lit in technical_literals):
            result.append(line)
            continue

        # Compress common verbose patterns
        compressed = line

        # "In order to" -> "To"
        compressed = re.sub(r"\bIn order to\b", "To", compressed, flags=re.IGNORECASE)

        # "Due to the fact that" -> "Because"
        compressed = re.sub(r"\bDue to the fact that\b", "Because", compressed, flags=re.IGNORECASE)

        # "At this point in time" -> "Now"
        compressed = re.sub(r"\bAt this point in time\b", "Now", compressed, flags=re.IGNORECASE)

        # "With regard to" -> "Regarding"
        compressed = re.sub(r"\bWith regard to\b", "Regarding", compressed, flags=re.IGNORECASE)

        # "In the event that" -> "If"
        compressed = re.sub(r"\bIn the event that\b", "If", compressed, flags=re.IGNORECASE)

        # "Make use of" -> "Use"
        compressed = re.sub(r"\bMake use of\b", "Use", compressed, flags=re.IGNORECASE)

        # "Provide an explanation of" -> "Explain"
        compressed = re.sub(r"\bProvide an explanation of\b", "Explain", compressed, flags=re.IGNORECASE)

        # "Give a description of" -> "Describe"
        compressed = re.sub(r"\bGive a description of\b", "Describe", compressed, flags=re.IGNORECASE)

        # Remove redundant "that" after verbs
        compressed = re.sub(
            r"\b(explain|describe|list|show|tell|indicate)\s+that\s+",
            r"\1 ",
            compressed,
            flags=re.IGNORECASE,
        )

        result.append(compressed)

    return "\n".join(result)


def _reorganize_sections(ctx: _OptimizationContext) -> None:
    """Reorganize sections for efficiency (move constraints earlier)."""
    original = "\n".join(ctx.lines)
    reorganized = _reorganize_sections_text(original)
    if reorganized != original:
        ctx.lines = reorganized.splitlines()
        ctx.transformations.append(
            Transformation(
                type="reorganize_sections",
                description="Reorganized sections for better token efficiency",
                original=original,
                optimized=reorganized,
                token_delta=0,
                risk_level=Severity.WARNING,
            )
        )


def _reorganize_sections_text(text: str) -> str:
    """Reorganize sections for efficiency (move constraints earlier)."""
    lines = text.splitlines()

    # Extract constraint-like lines
    constraint_lines = []
    other_lines = []

    constraint_keywords = [
        "must not", "never", "do not", "don't", "avoid",
        "prohibited", "forbidden", "constraint:", "requirement:",
    ]
    for line in lines:
        stripped = line.strip().lower()
        if any(kw in stripped for kw in constraint_keywords):
            constraint_lines.append(line)
        else:
            other_lines.append(line)

    # Put constraints first, then other content
    if constraint_lines:
        return "\n".join(constraint_lines + [""] + other_lines)

    return text


def _merge_short_lines(ctx: _OptimizationContext) -> None:
    """Merge adjacent short lines that are likely fragments."""
    original = "\n".join(ctx.lines)
    merged = _merge_short_lines_text(original)
    if merged != original:
        ctx.lines = merged.splitlines()
        ctx.transformations.append(
            Transformation(
                type="merge_short_lines",
                description="Merged adjacent short lines",
                original=original,
                optimized=merged,
                token_delta=0,
            )
        )


def _merge_short_lines_text(text: str) -> str:
    """Merge adjacent short lines that are likely fragments."""
    lines = text.splitlines()
    if len(lines) < 2:
        return text

    result = []
    i = 0
    while i < len(lines):
        current = lines[i]
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            # Merge if both are short and not headings/code/bullets
            if (
                len(current.strip()) < 60
                and len(next_line.strip()) < 60
                and current.strip()
                and next_line.strip()
                and not current.strip().startswith(("#", "-", "*", "`"))
                and not next_line.strip().startswith(("#", "-", "*", "`"))
                and not current.strip().endswith(":")
            ):
                merged = current.rstrip() + " " + next_line.lstrip()
                result.append(merged)
                i += 2
                continue
        result.append(current)
        i += 1

    return "\n".join(result)


# ============================================================================
# REGISTER TRANSFORMATIONS TO PROFILES
# ============================================================================

# Conservative: whitespace + duplicates only
register_transform(OptimizationProfile.CONSERVATIVE, _trim_trailing_whitespace)
register_transform(OptimizationProfile.CONSERVATIVE, _collapse_blank_lines)
register_transform(OptimizationProfile.CONSERVATIVE, _remove_exact_duplicates)
register_transform(OptimizationProfile.CONSERVATIVE, _trim_outer_blank_lines)

# Balanced: conservative + phrase consolidation + transitions + bullets + instruction consolidation
register_transform(OptimizationProfile.BALANCED, _trim_trailing_whitespace)
register_transform(OptimizationProfile.BALANCED, _collapse_blank_lines)
register_transform(OptimizationProfile.BALANCED, _remove_exact_duplicates)
register_transform(OptimizationProfile.BALANCED, _trim_outer_blank_lines)
register_transform(OptimizationProfile.BALANCED, _consolidate_repeated_phrases)
register_transform(OptimizationProfile.BALANCED, _remove_redundant_transitions)
register_transform(OptimizationProfile.BALANCED, _normalize_bullets)
register_transform(OptimizationProfile.BALANCED, _consolidate_similar_instructions)

# Aggressive: balanced + filler removal + compression + reorganization + line merging
register_transform(OptimizationProfile.AGGRESSIVE, _trim_trailing_whitespace)
register_transform(OptimizationProfile.AGGRESSIVE, _collapse_blank_lines)
register_transform(OptimizationProfile.AGGRESSIVE, _remove_exact_duplicates)
register_transform(OptimizationProfile.AGGRESSIVE, _trim_outer_blank_lines)
register_transform(OptimizationProfile.AGGRESSIVE, _consolidate_repeated_phrases)
register_transform(OptimizationProfile.AGGRESSIVE, _remove_redundant_transitions)
register_transform(OptimizationProfile.AGGRESSIVE, _normalize_bullets)
register_transform(OptimizationProfile.AGGRESSIVE, _consolidate_similar_instructions)
register_transform(OptimizationProfile.AGGRESSIVE, _remove_filler_sentences)
register_transform(OptimizationProfile.AGGRESSIVE, _compress_explanations)
register_transform(OptimizationProfile.AGGRESSIVE, _reorganize_sections)
register_transform(OptimizationProfile.AGGRESSIVE, _merge_short_lines)


__all__ = [
    "optimize_prompt",
    "OptimizationProfile",
    "register_transform",
    "PROFILE_TRANSFORMS",
]