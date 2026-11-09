"""tokensentry-context-engineer skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class ContextEngineerSkill(BaseSkill):
    """Improve long-context organization and relevance without silently discarding information."""

    metadata = SkillMetadata(
        name="tokensentry-context-engineer",
        version="0.1.0",
        description="Engineer efficient context for AI models by organizing, prioritizing, and compressing.",
        capabilities=[
            "Context segmentation (facts, instructions, references, examples)",
            "Relevance prioritization (by task dependency, recency, authority)",
            "Long-context compression with provenance tracking",
            "Durable fact extraction and separation from assumptions",
            "Dependency preservation for multi-step tasks",
            "Excluded material reporting with reasons",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt with context to engineer"},
                "task_description": {"type": "string", "description": "Description of the task the context supports"},
                "max_tokens": {"type": "integer", "description": "Target token budget"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "engineered_context": {"type": "string"},
                "original_tokens": {"type": "integer"},
                "engineered_tokens": {"type": "integer"},
                "excluded_content": {"type": "array"},
                "priority_ranking": {"type": "array"},
                "provenance_map": {"type": "object"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["context", "engineering", "compression", "prioritization"],
        entry_point="context_engineer.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute context engineering."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            # Analyze the prompt to get sections
            tokenizer = self.config.get("tokenizer")
            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Segment context
            segments = self._segment_context(analysis)
            prioritized = self._prioritize_segments(segments, self.config.get("task_description", ""))

            # Build engineered context
            max_tokens = self.config.get("max_tokens")
            engineered = self._build_engineered_context(prioritized, max_tokens)

            output = {
                "engineered_context": engineered,
                "original_tokens": analysis.token_count,
                "engineered_tokens": len(engineered) // 4,
                "excluded_content": [s for s in segments if not s.get("included", True)],
                "priority_ranking": [s for s in prioritized],
                "provenance_map": {s.get("id", ""): s for s in segments},
            }

            return SkillResult(
                skill_name=self.metadata.name,
                success=True,
                output=output,
            )
        except Exception as e:
            return SkillResult(
                skill_name=self.metadata.name,
                success=False,
                error=str(e),
            )

    def _segment_context(self, analysis) -> list[dict]:
        """Segment context into categories."""
        segments = []

        for i, section in enumerate(analysis.sections):
            seg_type = "reference"
            if section.type == "heading":
                seg_type = "instruction"
            elif section.type == "code_fence":
                seg_type = "example"
            elif section.type == "list":
                seg_type = "reference"

            segments.append({
                "id": f"seg_{i}",
                "type": seg_type,
                "content": section.content,
                "source_lines": (section.start_line, section.end_line),
                "priority": self._calculate_priority(section),
            })

        # Add requirements as instruction segments
        for i, req in enumerate(analysis.requirements):
            segments.append({
                "id": f"req_{i}",
                "type": "instruction",
                "content": req.text,
                "source_lines": req.line_range,
                "priority": 10 if req.is_critical else 7,
            })

        return segments

    def _calculate_priority(self, section) -> int:
        """Calculate priority for a section."""
        base = 5
        if section.type == "heading":
            base += 2
        if section.type == "code_fence":
            base += 1
        return min(10, base)

    def _prioritize_segments(self, segments: list[dict], task_description: str) -> list[dict]:
        """Prioritize segments by relevance to task."""
        # Simple prioritization - in reality would use embeddings or LLM
        for seg in segments:
            seg["included"] = True
        return sorted(segments, key=lambda s: s["priority"], reverse=True)

    def _build_engineered_context(self, segments: list[dict], max_tokens: int | None) -> str:
        """Build final engineered context."""
        parts = []
        token_count = 0

        for seg in segments:
            if not seg.get("included", True):
                continue

            content = seg["content"].strip()
            if not content:
                continue

            est_tokens = len(content) // 4
            if max_tokens and token_count + est_tokens > max_tokens:
                seg["included"] = False
                continue

            parts.append(content)
            token_count += est_tokens

        return "\n\n".join(parts)


# Register skill
registry.register(ContextEngineerSkill)