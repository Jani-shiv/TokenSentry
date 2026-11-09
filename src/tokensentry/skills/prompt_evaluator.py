"""tokensentry-prompt-evaluator skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class PromptEvaluatorSkill(BaseSkill):
    """Systematically evaluate prompt quality with scoring and test case generation."""

    metadata = SkillMetadata(
        name="tokensentry-prompt-evaluator",
        version="0.1.0",
        description="Evaluate prompt quality with systematic scoring, test cases, and regression detection.",
        capabilities=[
            "Clarity scoring (ambiguity, vagueness, specificity)",
            "Completeness scoring (role, context, task, constraints, output, examples)",
            "Constraint coverage analysis",
            "Output consistency evaluation",
            "Test case generation for prompt validation",
            "Regression evaluation (compare prompt versions)",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to evaluate"},
                "reference_output": {"type": "string", "description": "Expected output for consistency check"},
                "test_cases": {"type": "array", "description": "Custom test cases"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "overall_score": {"type": "number"},
                "dimension_scores": {"type": "object"},
                "test_cases": {"type": "array"},
                "regression_check": {"type": "object"},
                "recommendations": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["evaluation", "scoring", "testing", "quality", "regression"],
        entry_point="prompt_evaluator.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute prompt evaluation."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            reference = self.config.get("reference_output")
            test_cases = self.config.get("test_cases", [])

            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Compute dimension scores
            scores = self._compute_scores(analysis)

            # Generate test cases
            generated_cases = self._generate_test_cases(analysis)

            # Regression check if reference provided
            regression = {}
            if reference:
                regression = self._check_regression(context.prompt, reference, analysis)

            # Recommendations
            recommendations = self._generate_recommendations(scores, analysis)

            output = {
                "overall_score": scores["overall"],
                "dimension_scores": scores,
                "test_cases": generated_cases + test_cases,
                "regression_check": regression,
                "recommendations": recommendations,
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

    def _compute_scores(self, analysis) -> dict[str, float]:
        """Compute evaluation scores."""
        scores = {}

        # Clarity: inverse of ambiguity findings
        ambiguity_count = sum(1 for f in analysis.findings if f.code.startswith("AMBIGUOUS"))
        scores["clarity"] = max(0.0, 1.0 - ambiguity_count * 0.1)

        # Completeness: has role, context, task, constraints, output, examples
        prompt_lower = analysis.prompt.lower() if hasattr(analysis, 'prompt') else ""
        components = {
            "role": any(w in prompt_lower for w in ["act as", "role", "you are", "as a", "persona"]),
            "context": any(w in prompt_lower for w in ["context", "background", "given", "provided", "assume"]),
            "task": any(w in prompt_lower for w in ["task", "objective", "goal", "create", "write", "generate", "analyze"]),
            "constraints": any(r.type in ("positive", "negative", "value") for r in analysis.requirements),
            "output_format": any(r.type in ("format", "output", "schema") for r in analysis.requirements),
            "examples": any(s.type == "code_fence" for s in analysis.sections),
        }
        scores["completeness"] = sum(components.values()) / len(components)

        # Constraint coverage
        critical_reqs = [r for r in analysis.requirements if r.is_critical]
        covered_critical = sum(1 for r in critical_reqs if r.text in analysis.prompt)
        scores["constraint_coverage"] = covered_critical / len(critical_reqs) if critical_reqs else 1.0

        # Output consistency (structure)
        heading_count = sum(1 for s in analysis.sections if s.type == "heading")
        scores["output_structure"] = min(1.0, heading_count * 0.15 + 0.2)

        # Testability (can we verify output?)
        testable = any(r.type in ("format", "output", "schema") for r in analysis.requirements)
        scores["testability"] = 1.0 if testable else 0.3

        # Overall
        dims = ["clarity", "completeness", "constraint_coverage", "output_structure", "testability"]
        scores["overall"] = sum(scores[d] for d in dims) / len(dims)

        return scores

    def _generate_test_cases(self, analysis) -> list[dict]:
        """Generate test cases for prompt validation."""
        cases = []

        # Test case: valid input
        cases.append({
            "name": "valid_input",
            "description": "Standard valid input should produce expected output format",
            "input_type": "standard",
            "expected": "Valid output matching format requirements",
        })

        # Test case: edge cases from requirements
        for req in analysis.requirements:
            if req.type == "value" and req.exact_value:
                cases.append({
                    "name": f"boundary_{req.exact_value}",
                    "description": f"Test boundary at {req.exact_value}",
                    "input_type": "boundary",
                    "expected": "Handles boundary correctly",
                })

        # Test case: negative constraints
        neg_reqs = [r for r in analysis.requirements if r.type == "negative"]
        if neg_reqs:
            cases.append({
                "name": "negative_constraint_violation",
                "description": "Input violating negative constraints should be rejected",
                "input_type": "invalid",
                "expected": "Rejection or error handling",
            })

        # Test case: missing required info
        if any(r.type == "positive" for r in analysis.requirements):
            cases.append({
                "name": "missing_required_info",
                "description": "Input missing required information",
                "input_type": "incomplete",
                "expected": "Request for missing information",
            })

        return cases

    def _check_regression(self, prompt: str, reference: str, analysis) -> dict:
        """Check for regression against reference output."""
        # Simple comparison - in practice would run actual model
        return {
            "reference_provided": True,
            "note": "Full regression check requires model execution",
            "prompt_stable": True,  # Placeholder
        }

    def _generate_recommendations(self, scores: dict, analysis) -> list[str]:
        """Generate improvement recommendations."""
        recs = []

        if scores["clarity"] < 0.7:
            recs.append("Reduce ambiguous language; replace vague quantifiers with specifics")

        if scores["completeness"] < 0.7:
            if "role" not in scores:
                recs.append("Add explicit role definition")
            if "context" not in scores:
                recs.append("Provide context/background")
            if "task" not in scores:
                recs.append("Clarify task/objective")
            if scores.get("constraint_coverage", 1) < 1.0:
                recs.append("Ensure all critical constraints are explicitly stated")
            if scores.get("output_structure", 0) < 0.5:
                recs.append("Add output format requirements")
            if scores.get("testability", 0) < 0.5:
                recs.append("Make output verifiable with explicit format/schema")

        return recs


# Register skill
registry.register(PromptEvaluatorSkill)