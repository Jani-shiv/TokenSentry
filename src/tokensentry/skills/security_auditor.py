"""tokensentry-prompt-security-auditor skill implementation."""

from __future__ import annotations

from tokensentry.core.analyzer import analyze_prompt
from tokensentry.models import SkillMetadata
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult, registry


class PromptSecurityAuditorSkill(BaseSkill):
    """Audit prompts for security risks including injection, secrets, and unsafe instructions."""

    metadata = SkillMetadata(
        name="tokensentry-prompt-security-auditor",
        version="0.1.0",
        description="Comprehensive security audit of prompts for injection, secrets, and unsafe patterns.",
        capabilities=[
            "Prompt injection detection (instruction override, role hijacking, continuation attacks)",
            "Secret/credential exposure detection (API keys, tokens, passwords, cloud keys)",
            "Unsafe instruction detection (command execution, file operations, network requests)",
            "Data leakage risk analysis (PII, internal endpoints, git metadata)",
            "Privilege escalation attempt detection",
            "Untrusted content boundary analysis",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to audit"},
                "tokenizer": {"type": "string", "description": "Tokenizer to use"},
                "strict_mode": {"type": "boolean", "default": False, "description": "Enable strict security checks"},
            },
            "required": ["prompt"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "findings": {"type": "array"},
                "injection_risks": {"type": "array"},
                "secret_exposures": {"type": "array"},
                "unsafe_instructions": {"type": "array"},
                "data_leakage_risks": {"type": "array"},
                "privilege_escalation": {"type": "array"},
                "boundary_issues": {"type": "array"},
                "recommendations": {"type": "array"},
            },
        },
        dependencies=["tokensentry-analyzer"],
        tags=["security", "audit", "injection", "secrets", "safety"],
        entry_point="prompt_security_auditor.py",
        min_tokensentry_version="0.1.0",
    )

    def execute(self, context: SkillContext) -> SkillResult:
        """Execute security audit."""
        try:
            if not self.validate_input(context):
                return SkillResult(
                    skill_name=self.metadata.name,
                    success=False,
                    error="Invalid input: prompt is required",
                )

            tokenizer = self.config.get("tokenizer")
            strict = self.config.get("strict_mode", False)

            # Use analyzer to get security findings
            analysis = analyze_prompt(context.prompt, tokenizer_name=tokenizer)

            # Extract security findings
            security_findings = [f for f in analysis.findings if f.code.startswith("SECURITY_") or f.code.startswith("PROMPT_INJECTION") or f.code.startswith("SECRET_") or f.code.startswith("UNSAFE_") or f.code.startswith("DATA_LEAKAGE") or f.code.startswith("PRIVILEGE_") or f.code.startswith("BOUNDARY_")]

            # Categorize findings
            categories = {
                "injection_risks": [],
                "secret_exposures": [],
                "unsafe_instructions": [],
                "data_leakage_risks": [],
                "privilege_escalation": [],
                "boundary_issues": [],
            }

            for f in security_findings:
                code = f.code
                if code.startswith("PROMPT_INJECTION"):
                    categories["injection_risks"].append(f.model_dump())
                elif code.startswith("SECRET_EXPOSURE"):
                    categories["secret_exposures"].append(f.model_dump())
                elif code.startswith("UNSAFE_INSTRUCTION"):
                    categories["unsafe_instructions"].append(f.model_dump())
                elif code.startswith("DATA_LEAKAGE"):
                    categories["data_leakage_risks"].append(f.model_dump())
                elif code.startswith("PRIVILEGE_ESCALATION"):
                    categories["privilege_escalation"].append(f.model_dump())
                elif code.startswith("BOUNDARY_ISSUE"):
                    categories["boundary_issues"].append(f.model_dump())

            # Calculate overall risk level
            risk_counts = {k: len(v) for k, v in categories.items()}
            total_critical = sum(1 for cat in categories.values() for f in cat if f.get("severity") == "error" or f.get("severity") == "critical")
            total_warnings = sum(1 for cat in categories.values() for f in cat if f.get("severity") == "warning")

            if total_critical > 2:
                risk_level = "critical"
            elif total_critical > 0 or total_warnings > 3:
                risk_level = "high"
            elif total_warnings > 0:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Generate recommendations
            recommendations = []
            if categories["injection_risks"]:
                recommendations.append("Sanitize user input boundaries; use explicit delimiters for untrusted content")
            if categories["secret_exposures"]:
                recommendations.append("Remove all secrets from prompts; use environment variables or secret managers")
            if categories["unsafe_instructions"]:
                recommendations.append("Avoid instructing models to execute commands or access sensitive systems")
            if categories["data_leakage_risks"]:
                recommendations.append("Remove PII and internal infrastructure details from prompts")
            if categories["privilege_escalation"]:
                recommendations.append("Reject prompts attempting to escalate privileges or bypass security")
            if categories["boundary_issues"]:
                recommendations.append("Clearly demarcate untrusted content with explicit boundaries")

            output = {
                "risk_level": risk_level,
                "findings": [f.model_dump() for f in security_findings],
                **categories,
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


# Register skill
registry.register(PromptSecurityAuditorSkill)