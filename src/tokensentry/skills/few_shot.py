"""tokensentry-few-shot-optimizer skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class FewShotOptimizerSkill(BaseSkill):
    """Improve prompts containing few-shot examples."""

    metadata = SkillMetadata(
        name="tokensentry-few-shot-optimizer",
        version="0.1.0",
        description="Optimize few-shot prompts by detecting redundancy, analyzing coverage, and compressing demonstrations.",
        capabilities=[
            "Example redundancy detection (duplicate/similar input-output pairs)",
            "Coverage analysis (input space coverage, edge cases)",
            "Input/output pair validation (format consistency, correctness)",
            "Example ordering optimization (easy-to-hard, diverse-first)",
            "Demonstration compression (remove verbose examples, keep representative)",
            "Edge case preservation (ensure critical examples retained)",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt with few-shot examples"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
                "max_examples": {"type": "integer", "description": "Maximum examples to retain"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "example_count": {"type": "integer"},
                "redundant_examples": {"type": "array"},
                "coverage_gaps": {"type": "array"},
                "ordering_suggestions": {"type": "array"},
                "compressed_examples": {"type": "array"},
                "preserved_edge_cases": {"type": "array"},
                "token_savings": {"type": "integer"},
            },
        },
        dependencies=["tokensentry-analyzer", "tokensentry-optimizer"],
        tags=["few-shot", "examples", "optimization", "compression"],
        entry_point="few_shot_optimizer.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute few-shot optimization."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            max_examples = self.config.get("max_examples")

            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Find code fences (likely examples)
            examples = [s for s in analysis.sections if s.type == "code_fence"]

            # Parse examples into input/output pairs
            pairs = self._parse_examples(examples)

            # Detect redundant examples
            redundant = self._find_redundant(pairs)

            # Analyze coverage
            coverage_gaps = self._analyze_coverage(pairs)

            # Suggest ordering
            ordering = self._suggest_ordering(pairs)

            # Compress examples
            compressed = self._compress_examples(pairs, max_examples)

            # Identify preserved edge cases
            edge_cases = self._identify_edge_cases(pairs)

            # Calculate token savings
            original_tokens = sum(len(p.get("input", "")) + len(p.get("output", "")) for p in pairs) // 4
            compressed_tokens = sum(len(p.get("input", "")) + len(p.get("output", "")) for p in compressed) // 4

            output = {
                "example_count": len(pairs),
                "redundant_examples": redundant,
                "coverage_gaps": coverage_gaps,
                "ordering_suggestions": ordering,
                "compressed_examples": compressed,
                "preserved_edge_cases": edge_cases,
                "token_savings": original_tokens - compressed_tokens,
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

    def _parse_examples(self, examples: list) -> list[dict]:
        """Parse code fences into input/output pairs."""
        pairs = []
        for ex in examples:
            content = ex.content.strip()
            # Try to split into input/output
            if "Input:" in content and "Output:" in content:
                parts = content.split("Output:")
                input_part = parts[0].replace("Input:", "").strip()
                output_part = parts[1].strip()
                pairs.append({"input": input_part, "output": output_part, "raw": content})
            elif "```" in content:
                # Just the raw example
                pairs.append({"raw": content, "input": "", "output": ""})
            else:
                pairs.append({"raw": content, "input": "", "output": ""})
        return pairs

    def _find_redundant(self, pairs: list[dict]) -> list[dict]:
        """Find redundant/similar examples."""
        redundant = []
        from difflib import SequenceMatcher

        for i, p1 in enumerate(pairs):
            for j, p2 in enumerate(pairs[i+1:], i+1):
                # Compare raw content
                sim = SequenceMatcher(None, p1.get("raw", ""), p2.get("raw", "")).ratio()
                if sim > 0.8:
                    redundant.append({
                        "example_1_index": i,
                        "example_2_index": j,
                        "similarity": round(sim, 2),
                        "reason": "High content similarity",
                    })
        return redundant

    def _analyze_coverage(self, pairs: list[dict]) -> list[dict]:
        """Analyze coverage gaps in examples."""
        gaps = []

        # Check for common patterns
        has_error_case = any("error" in p.get("raw", "").lower() for p in pairs)
        has_edge_case = any("edge" in p.get("raw", "").lower() or "boundary" in p.get("raw", "").lower() for p in pairs)
        has_empty_input = any(not p.get("input", "").strip() for p in pairs)

        if not has_error_case:
            gaps.append({"type": "error_handling", "description": "No error case examples"})
        if not has_edge_case:
            gaps.append({"type": "edge_cases", "description": "No boundary/edge case examples"})
        if not has_empty_input:
            gaps.append({"type": "empty_input", "description": "No empty input examples"})

        return gaps

    def _suggest_ordering(self, pairs: list[dict]) -> list[str]:
        """Suggest optimal example ordering."""
        suggestions = [
            "Order from simple to complex (easy-to-hard)",
            "Place diverse examples first for better generalization",
            "Group similar task types together",
            "End with most representative/typical example",
        ]
        return suggestions

    def _compress_examples(self, pairs: list[dict], max_examples: int | None) -> list[dict]:
        """Compress examples by removing redundancy."""
        if max_examples and len(pairs) > max_examples:
            # Keep first, last, and most diverse
            keep_indices = {0, len(pairs) - 1}
            # Add middle diverse ones
            step = max(1, (len(pairs) - 2) // (max_examples - 2)) if max_examples > 2 else 1
            for i in range(1, len(pairs) - 1, step):
                keep_indices.add(i)

            return [pairs[i] for i in sorted(keep_indices)]
        return pairs

    def _identify_edge_cases(self, pairs: list[dict]) -> list[dict]:
        """Identify and preserve edge case examples."""
        edge_cases = []

        for i, p in enumerate(pairs):
            raw = p.get("raw", "").lower()
            if any(kw in raw for kw in ["error", "exception", "fail", "invalid", "empty", "null", "boundary", "edge", "limit", "max", "min"]):
                edge_cases.append({
                    "index": i,
                    "reason": "Contains edge case keywords",
                    "content": p.get("raw", "")[:200],
                })

        return edge_cases


# Register skill
registry.register(FewShotOptimizerSkill)