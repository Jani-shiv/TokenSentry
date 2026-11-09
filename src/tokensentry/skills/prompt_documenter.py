"""tokensentry-prompt-documenter skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class PromptDocumenterSkill(BaseSkill):
    """Generate maintainable documentation for prompts."""

    metadata = SkillMetadata(
        name="tokensentry-prompt-documenter",
        version="0.1.0",
        description="Generate comprehensive prompt documentation with purpose, variables, constraints, and examples.",
        capabilities=[
            "Document prompt purpose and intent",
            "Extract and document variables/parameters",
            "Document all constraints and requirements",
            "Describe expected output format",
            "Generate usage examples",
            "Track prompt versions and changes",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to document"},
                "version": {"type": "string", "default": "1.0.0", "description": "Prompt version"},
                "author": {"type": "string", "description": "Document author"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "metadata": {"type": "object"},
                "sections": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["documentation", "maintainability", "versioning", "knowledge"],
        entry_point="prompt_documenter.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Generate prompt documentation."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            version = self.config.get("version", "1.0.0")
            author = self.config.get("author", "TokenSentry")

            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Build documentation sections
            sections = self._build_sections(analysis, version, author)

            # Generate full markdown documentation
            doc = self._generate_markdown(sections, analysis)

            output = {
                "documentation": doc,
                "metadata": {
                    "version": version,
                    "author": author,
                    "generated_by": "tokensentry-prompt-documenter",
                    "prompt_id": analysis.prompt_id,
                    "token_count": analysis.token_count,
                },
                "sections": sections,
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

    def _build_sections(self, analysis, version: str, author: str) -> list[dict]:
        """Build documentation sections."""
        sections = []

        # 1. Overview
        sections.append({
            "title": "Overview",
            "content": (
                f"**Prompt ID:** {analysis.prompt_id}\n"
                f"**Version:** {version}\n"
                f"**Author:** {author}\n"
                f"**Token Count:** {analysis.token_count} ({analysis.tokenizer.count_kind})\n"
                f"**Tokenizer:** {analysis.tokenizer.name}\n"
                f"**Quality Score:** {analysis.quality_scores.get('overall', 0):.2f}/1.00"
            ),
        })

        # 2. Purpose
        purpose = self._extract_purpose(analysis)
        sections.append({
            "title": "Purpose",
            "content": purpose or "Purpose not explicitly stated in prompt.",
        })

        # 3. Variables/Parameters
        variables = self._extract_variables(analysis)
        if variables:
            var_content = "\n".join(f"- **{v['name']}**: {v['description']} ({v['type']})" for v in variables)
            sections.append({
                "title": "Variables",
                "content": var_content,
            })

        # 4. Constraints & Requirements
        constraints = self._format_requirements(analysis.requirements)
        if constraints:
            sections.append({
                "title": "Constraints & Requirements",
                "content": constraints,
            })

        # 5. Output Format
        output_format = self._extract_output_format(analysis)
        if output_format:
            sections.append({
                "title": "Expected Output Format",
                "content": output_format,
            })

        # 6. Examples
        examples = self._format_examples(analysis.sections)
        if examples:
            sections.append({
                "title": "Examples",
                "content": examples,
            })

        # 7. Technical Literals
        literals = self._format_literals(analysis.technical_literals)
        if literals:
            sections.append({
                "title": "Technical Literals (Must Preserve)",
                "content": literals,
            })

        # 8. Quality Metrics
        quality = self._format_quality(analysis.quality_scores)
        sections.append({
            "title": "Quality Metrics",
            "content": quality,
        })

        # 9. Findings & Warnings
        findings = self._format_findings(analysis.findings)
        if findings:
            sections.append({
                "title": "Analysis Findings",
                "content": findings,
            })

        return sections

    def _extract_purpose(self, analysis) -> str:
        """Extract prompt purpose from first paragraph or role statement."""
        prompt = analysis.prompt if hasattr(analysis, 'prompt') else ""
        lines = [l.strip() for l in prompt.splitlines() if l.strip()]

        for line in lines:
            if any(kw in line.lower() for kw in ["act as", "role", "you are", "task", "objective", "goal"]):
                return line

        return lines[0] if lines else "No clear purpose statement found."

    def _extract_variables(self, analysis) -> list[dict]:
        """Extract variable-like patterns."""
        variables = []
        prompt = analysis.prompt if hasattr(analysis, 'prompt') else ""

        import re
        # Look for {{variable}}, {variable}, $VARIABLE patterns
        patterns = [
            (r"\{\{(\w+)\}\}", "template"),
            (r"\{(\w+)\}", "placeholder"),
            (r"\$(\w+)", "env_var"),
        ]

        for pattern, var_type in patterns:
            for match in re.finditer(pattern, prompt):
                variables.append({
                    "name": match.group(1),
                    "type": var_type,
                    "description": f"{var_type.capitalize()} variable",
                })

        return variables

    def _format_requirements(self, requirements) -> str:
        """Format requirements for documentation."""
        if not requirements:
            return ""

        by_type = {}
        for req in requirements:
            by_type.setdefault(req.type, []).append(req.text)

        parts = []
        for req_type, reqs in by_type.items():
            type_label = req_type.capitalize()
            parts.append(f"### {type_label} Constraints")
            for req in reqs:
                parts.append(f"- {req}")
            parts.append("")

        return "\n".join(parts)

    def _extract_output_format(self, analysis) -> str:
        """Extract output format requirements."""
        formats = []
        for req in analysis.requirements:
            if req.type in ("format", "output", "schema"):
                formats.append(req.text)
        return "\n".join(f"- {f}" for f in formats) if formats else ""

    def _format_examples(self, sections) -> str:
        """Format code fence examples."""
        examples = [s for s in sections if s.type == "code_fence"]
        if not examples:
            return ""

        parts = []
        for i, ex in enumerate(examples, 1):
            lang = ex.language or ""
            parts.append(f"#### Example {i} ({lang})")
            parts.append(f"```{lang}\n{ex.content.strip()}\n```")
            parts.append("")

        return "\n".join(parts)

    def _format_literals(self, literals) -> str:
        """Format technical literals."""
        if not literals:
            return ""

        by_type = {}
        for lit in literals:
            by_type.setdefault(lit.type, []).append(lit.value)

        parts = []
        for lit_type, values in by_type.items():
            parts.append(f"### {lit_type.capitalize()}")
            for v in values:
                parts.append(f"- `{v}`")
            parts.append("")

        return "\n".join(parts)

    def _format_quality(self, scores: dict) -> str:
        """Format quality scores."""
        if not scores:
            return "No quality scores available."

        parts = ["| Dimension | Score |", "|-----------|-------|"]
        for dim, score in scores.items():
            if dim != "overall":
                parts.append(f"| {dim.capitalize()} | {score:.2f} |")
        parts.append(f"| **Overall** | **{scores.get('overall', 0):.2f}** |")
        return "\n".join(parts)

    def _format_findings(self, findings) -> str:
        """Format findings for documentation."""
        if not findings:
            return "No significant findings."

        by_severity = {}
        for f in findings:
            by_type.setdefault(f.severity, []).append(f)

        parts = []
        for severity in ["critical", "error", "warning", "info"]:
            if severity in by_type:
                parts.append(f"### {severity.capitalize()}")
                for f in by_type[severity]:
                    parts.append(f"- **{f.code}**: {f.message}")
                    if f.suggestion:
                        parts.append(f"  - *Suggestion*: {f.suggestion}")
                parts.append("")

        return "\n".join(parts)

    def _generate_markdown(self, sections: list[dict], analysis) -> str:
        """Generate full markdown documentation."""
        lines = [
            f"# Prompt Documentation: {analysis.prompt_id}",
            "",
            f"*Generated by TokenSentry Prompt Documenter*",
            "",
        ]

        for section in sections:
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(section['content'])
            lines.append("")

        return "\n".join(lines)


# Register skill
registry.register(PromptDocumenterSkill)