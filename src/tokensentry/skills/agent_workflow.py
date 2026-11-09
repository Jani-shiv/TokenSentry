"""tokensentry-agent-workflow skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class AgentWorkflowSkill(BaseSkill):
    """Optimize instructions used by AI agents and multi-step workflows."""

    metadata = SkillMetadata(
        name="tokensentry-agent-workflow",
        version="0.1.0",
        description="Analyze and optimize multi-step agent workflows, tool usage, and state management.",
        capabilities=[
            "Multi-step workflow analysis (sequential, parallel, conditional)",
            "Tool usage instruction analysis (availability, parameters, error handling)",
            "Dependency detection between steps",
            "State and memory requirement analysis",
            "Error handling and retry logic validation",
            "Completion criteria verification",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Agent workflow prompt"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "workflow_steps": {"type": "array"},
                "tool_usage": {"type": "array"},
                "dependencies": {"type": "array"},
                "state_requirements": {"type": "array"},
                "error_handling": {"type": "array"},
                "completion_criteria": {"type": "array"},
                "optimization_suggestions": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["agent", "workflow", "multi-step", "tools", "orchestration"],
        entry_point="agent_workflow.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute agent workflow analysis."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Extract workflow steps
            steps = self._extract_workflow_steps(analysis)

            # Analyze tool usage
            tools = self._analyze_tool_usage(analysis)

            # Detect dependencies
            dependencies = self._detect_dependencies(steps)

            # Analyze state requirements
            state_reqs = self._analyze_state_requirements(analysis)

            # Check error handling
            error_handling = self._check_error_handling(analysis)

            # Verify completion criteria
            completion = self._verify_completion_criteria(analysis)

            # Generate suggestions
            suggestions = self._generate_suggestions(steps, tools, dependencies, state_reqs, error_handling, completion)

            output = {
                "workflow_steps": steps,
                "tool_usage": tools,
                "dependencies": dependencies,
                "state_requirements": state_reqs,
                "error_handling": error_handling,
                "completion_criteria": completion,
                "optimization_suggestions": suggestions,
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

    def _extract_workflow_steps(self, analysis) -> list[dict]:
        """Extract workflow steps from prompt."""
        steps = []

        # Look for numbered steps or explicit workflow language
        lines = analysis.prompt.splitlines() if hasattr(analysis, 'prompt') else []
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Numbered steps
            if stripped and (stripped[0].isdigit() and stripped[1:3] in (". ", ") ")):
                steps.append({
                    "index": len(steps) + 1,
                    "description": stripped,
                    "line": i + 1,
                })
            # Explicit step markers
            elif any(kw in stripped.lower() for kw in ["step ", "phase ", "stage ", "then ", "next "]):
                steps.append({
                    "index": len(steps) + 1,
                    "description": stripped,
                    "line": i + 1,
                })

        # Also check requirements for workflow-like instructions
        for req in analysis.requirements:
            if req.type == "positive" and any(kw in req.text.lower() for kw in ["step", "phase", "then", "after", "before"]):
                steps.append({
                    "index": len(steps) + 1,
                    "description": req.text,
                    "source": "requirement",
                })

        return steps

    def _analyze_tool_usage(self, analysis) -> list[dict]:
        """Analyze tool usage instructions."""
        tools = []

        for literal in analysis.technical_literals:
            if literal.type == "command":
                tools.append({
                    "command": literal.value,
                    "context": literal.context,
                    "line": literal.line_range[0] if literal.line_range else None,
                })

        # Also check for tool mentions in requirements
        for req in analysis.requirements:
            if "tool" in req.text.lower() or "function" in req.text.lower() or "api" in req.text.lower():
                tools.append({
                    "description": req.text,
                    "source": "requirement",
                })

        return tools

    def _detect_dependencies(self, steps: list[dict]) -> list[dict]:
        """Detect dependencies between workflow steps."""
        deps = []

        for i, step in enumerate(steps):
            desc = step.get("description", "").lower()
            # Look for references to previous steps
            if any(kw in desc for kw in ["previous", "above", "before", "after", "then", "result", "output"]):
                deps.append({
                    "step": i + 1,
                    "depends_on": "previous" if i > 0 else None,
                    "type": "sequential",
                })

        return deps

    def _analyze_state_requirements(self, analysis) -> list[dict]:
        """Analyze state/memory requirements."""
        state = []

        prompt_lower = analysis.prompt.lower() if hasattr(analysis, 'prompt') else ""

        if "remember" in prompt_lower or "memory" in prompt_lower or "context" in prompt_lower:
            state.append({"type": "memory", "description": "Prompt references memory/remembering"})

        if "variable" in prompt_lower or "state" in prompt_lower:
            state.append({"type": "state", "description": "Prompt references state/variables"})

        if "session" in prompt_lower or "history" in prompt_lower:
            state.append({"type": "session", "description": "Prompt references session/history"})

        return state

    def _check_error_handling(self, analysis) -> list[dict]:
        """Check for error handling instructions."""
        error_handling = []

        prompt_lower = analysis.prompt.lower() if hasattr(analysis, 'prompt') else ""

        error_keywords = ["error", "exception", "fail", "retry", "catch", "handle", "fallback"]
        for kw in error_keywords:
            if kw in prompt_lower:
                error_handling.append({"keyword": kw, "description": f"References {kw} handling"})

        return error_handling

    def _verify_completion_criteria(self, analysis) -> list[dict]:
        """Verify completion criteria are defined."""
        criteria = []

        prompt_lower = analysis.prompt.lower() if hasattr(analysis, 'prompt') else ""

        completion_keywords = ["done", "complete", "finish", "final", "result", "output", "return"]
        for kw in completion_keywords:
            if kw in prompt_lower:
                criteria.append({"keyword": kw, "description": f"References {kw}"})

        return criteria

    def _generate_suggestions(self, steps, tools, deps, state, errors, completion) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []

        if len(steps) > 10:
            suggestions.append("Consider breaking large workflows into sub-workflows")

        if not deps and len(steps) > 1:
            suggestions.append("Add explicit dependencies between workflow steps")

        if not state:
            suggestions.append("Define state/memory requirements explicitly")

        if not errors:
            suggestions.append("Add error handling and retry logic for tool calls")

        if not completion:
            suggestions.append("Define explicit completion criteria")

        if tools and len(tools) > 5:
            suggestions.append("Consider grouping related tools into skill sets")

        return suggestions


# Register skill
registry.register(AgentWorkflowSkill)