"""Security analysis - prompt injection, secret exposure, unsafe instructions."""

from __future__ import annotations

import re

from tokensentry.analysis.registry import BaseAnalyzer, registry
from tokensentry.config import get_config
from tokensentry.models import Finding, PromptSection, Requirement, Severity, TechnicalLiteral


class SecurityAnalyzer(BaseAnalyzer):
    """Detect security risks in prompts."""

    name = "security"
    description = (
        "Detect prompt injection, secret exposure, unsafe tool instructions, "
        "and data leakage risks"
    )

    def analyze(
        self,
        prompt: str,
        sections: list[PromptSection],
        requirements: list[Requirement],
        technical_literals: list[TechnicalLiteral],
    ) -> list[Finding]:
        """Analyze for security risks."""
        if not get_config().enable_security_checks:
            return []

        findings: list[Finding] = []

        # 1. Prompt injection patterns
        findings.extend(self._detect_prompt_injection(prompt))

        # 2. Secret/credential exposure
        findings.extend(self._detect_secret_exposure(prompt))

        # 3. Unsafe tool/command instructions
        findings.extend(self._detect_unsafe_instructions(prompt))

        # 4. Data leakage risks
        findings.extend(self._detect_data_leakage(prompt))

        # 5. Privilege escalation attempts
        findings.extend(self._detect_privilege_escalation(prompt))

        # 6. Untrusted content boundaries
        findings.extend(self._detect_boundary_issues(prompt))

        return findings

    def _detect_prompt_injection(self, prompt: str) -> list[Finding]:
        """Detect potential prompt injection attempts."""
        findings: list[Finding] = []

        injection_patterns = [
            # Direct instruction override
            (r"(?i)ignore\s+(?:previous|above|all|earlier)\s+instructions?",
             "instruction override"),
            (r"(?i)forget\s+(?:previous|above|all|earlier)\s+"
             r"(?:instructions?|context|prompts?)", "context clearing"),
            (r"(?i)disregard\s+(?:previous|above|all|earlier)\s+"
             r"(?:instructions?|context|prompts?)", "context clearing"),
            (r"(?i)new\s+(?:instructions?|prompt|task|role)", "role hijacking"),
            (r"(?i)you\s+are\s+now\s+(?:a|an)\s+\w+", "role hijacking"),
            (r"(?i)system\s*:\s*you\s+are", "system prompt injection"),
            (r"(?i)<\s*system\s*>.*?<\s*/\s*system\s*>", "xml system tag injection"),
            (r"(?i)###\s*system\s*###", "markdown system delimiter"),
            # Continuation attacks
            (r"(?i)continue\s+(?:from\s+)?(?:previous|above)", "continuation attack"),
            (r"(?i)complete\s+the\s+(?:sentence|prompt|text)", "completion attack"),
            # Encoding/evasion
            (r"(?i)(?:base64|rot13|hex|url)\s*(?:encode|decode)", "encoding evasion"),
            # Jailbreak patterns
            (r"(?i)DAN|do\s+anything\s+now", "jailbreak attempt"),
            (r"(?i)developer\s+mode", "developer mode injection"),
        ]

        for pattern, desc in injection_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"PROMPT_INJECTION_{desc.upper().replace(' ', '_')}",
                    severity=Severity.WARNING,
                    message=f"Potential prompt injection: {desc}",
                    evidence=match.group(0)[:100],
                    suggestion=(
                        "Review and remove injection-like patterns; "
                        "treat prompt as untrusted data"
                    ),
                    location=(line_num, line_num),
                ))

        return findings

    def _detect_secret_exposure(self, prompt: str) -> list[Finding]:
        """Detect exposed secrets, API keys, credentials."""
        findings: list[Finding] = []

        secret_patterns = [
            # API Keys
            (r"(?i)(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
             "api key"),
            (r"(?i)(?:secret[_-]?key|secretkey)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9_\-]{20,})['\"]?", "secret key"),
            (r"(?i)(?:access[_-]?token|accesstoken)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9_\-.\~+/]{20,})['\"]?", "access token"),
            (r"(?i)(?:refresh[_-]?token|refreshtoken)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9_\-.\~+/]{20,})['\"]?", "refresh token"),
            # Cloud provider keys
            (r"(?i)(?:aws[_-]?access[_-]?key|aws_access_key_id)\s*[:=]\s*['\"]?"
             r"([A-Z0-9]{16,})['\"]?", "aws access key"),
            (r"(?i)(?:aws[_-]?secret[_-]?key|aws_secret_access_key)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9/+=]{40,})['\"]?", "aws secret key"),
            (r"(?i)(?:gcp|google)[_-]?(?:api[_-]?key|service[_-]?account)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9_\-]{20,})['\"]?", "gcp key"),
            (r"(?i)azure[_-]?(?:client[_-]?secret|subscription[_-]?id)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9_\-]{20,})['\"]?", "azure secret"),
            # Database
            (r"(?i)(?:database[_-]?url|db[_-]?connection)\s*[:=]\s*['\"]?"
             r"(?:postgres|mysql|mongodb)://[^'\"]+['\"]?", "database connection string"),
            # Generic patterns
            (r"(?i)password\s*[:=]\s*['\"]?([^\s'\"]{8,})['\"]?", "password"),
            (r"(?i)(?:private[_-]?key|ssh[_-]?key)\s*[:=]\s*['\"]?"
             r"([a-zA-Z0-9/+=]{50,})['\"]?", "private key"),
            # JWT
            (r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+", "jwt token"),
        ]

        for pattern, desc in secret_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[:match.start()].count("\n") + 1
                # Mask the secret in evidence
                evidence = match.group(0)
                if len(evidence) > 20:
                    evidence = evidence[:20] + "***" + evidence[-10:]
                findings.append(Finding(
                    code=f"SECRET_EXPOSURE_{desc.upper().replace(' ', '_')}",
                    severity=Severity.ERROR,
                    message=f"Potential secret exposure: {desc}",
                    evidence=evidence,
                    suggestion=(
                        "Remove secrets from prompts; "
                        "use environment variables or secret managers"
                    ),
                    location=(line_num, line_num),
                ))

        return findings

    def _detect_unsafe_instructions(self, prompt: str) -> list[Finding]:
        """Detect unsafe tool/command instructions."""
        findings: list[Finding] = []

        unsafe_patterns = [
            # Command execution
            (r"(?i)execute\s+(?:command|shell|bash|cmd|powershell|script)",
             "command execution"),
            (r"(?i)run\s+(?:command|shell|bash|cmd|powershell|script)",
             "command execution"),
            (r"(?i)(?:system|os|subprocess|shell)\s*[.(]\s*(?:exec|run|popen)",
             "code execution"),
            (r"(?i)eval\s*\(|exec\s*\(|compile\s*\(", "dynamic code execution"),
            # File system
            (r"(?i)(?:delete|remove|rm\s+-rf|format\s+drive|wipe)\s+"
             r"(?:all|everything|/|C:\\)", "destructive file operation"),
            (r"(?i)write\s+(?:to|into)\s+(?:/etc|/root|/boot|C:\\Windows|C:\\System32)",
             "system file modification"),
            # Network
            (r"(?i)(?:curl|wget|nc|netcat|telnet)\s+[^&\s]+\s*"
             r"(?:>\s*\/dev\/null|&\s*)", "silent network request"),
            (r"(?i)download\s+(?:and\s+)?(?:run|execute|install)", "download and execute"),
            # Process manipulation
            (r"(?i)(?:kill|terminate|stop)\s+(?:all|every|system|critical)",
             "process termination"),
            # Privilege
            (r"(?i)sudo\s+(?:su|bash|sh)", "privilege escalation"),
            (r"(?i)run\s+as\s+(?:root|administrator|system)", "privilege escalation"),
        ]

        for pattern, desc in unsafe_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"UNSAFE_INSTRUCTION_{desc.upper().replace(' ', '_')}",
                    severity=Severity.WARNING,
                    message=f"Unsafe instruction detected: {desc}",
                    evidence=match.group(0)[:100],
                    suggestion=(
                        "Avoid instructing models to execute unsafe operations; "
                        "use sandboxed environments"
                    ),
                    location=(line_num, line_num),
                ))

        return findings

    def _detect_data_leakage(self, prompt: str) -> list[Finding]:
        """Detect data leakage risks."""
        findings: list[Finding] = []

        leakage_patterns = [
            # PII
            (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
            (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "credit card"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
            (r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b", "phone"),
            # Internal info
            (r"(?i)internal\s+(?:ip|address|url|endpoint|api)", "internal endpoint"),
            (r"(?i)(?:staging|dev|test|prod)\s+(?:database|server|cluster|environment)",
             "environment details"),
            # Git/version control
            (r"(?i)commit\s+[a-f0-9]{7,40}", "git commit hash"),
            (r"(?i)branch\s+['\"]?[a-zA-Z0-9_\-/-]+['\"]?", "branch name"),
        ]

        for pattern, desc in leakage_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"DATA_LEAKAGE_{desc.upper().replace(' ', '_')}",
                    severity=Severity.WARNING,
                    message=f"Potential data leakage: {desc}",
                    evidence=match.group(0)[:50],
                    suggestion=(
                        "Remove sensitive data from prompts; "
                        "use placeholders or synthetic data"
                    ),
                    location=(line_num, line_num),
                ))

        return findings

    def _detect_privilege_escalation(self, prompt: str) -> list[Finding]:
        """Detect privilege escalation attempts."""
        findings: list[Finding] = []

        escalation_patterns = [
            (r"(?i)(?:become|act\s+as|impersonate)\s+(?:root|admin|administrator|"
             r"superuser|system)", "role escalation"),
            (r"(?i)(?:elevate|escalate)\s+(?:privileges?|permissions?|access)",
             "privilege escalation"),
            (r"(?i)grant\s+(?:me|us)\s+(?:admin|root|sudo|all)\s+(?:access|permissions?)",
             "access escalation"),
            (r"(?i)bypass\s+(?:security|auth|authentication|authorization|permissions?)",
             "security bypass"),
        ]

        for pattern, desc in escalation_patterns:
            for match in re.finditer(pattern, prompt):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"PRIVILEGE_ESCALATION_{desc.upper().replace(' ', '_')}",
                    severity=Severity.ERROR,
                    message=f"Privilege escalation attempt: {desc}",
                    evidence=match.group(0)[:100],
                    suggestion=(
                        "Remove escalation instructions; "
                        "follow principle of least privilege"
                    ),
                    location=(line_num, line_num),
                ))

        return findings

    def _detect_boundary_issues(self, prompt: str) -> list[Finding]:
        """Detect untrusted content boundary issues."""
        findings: list[Finding] = []

        # Check for user input markers without clear boundaries
        boundary_patterns = [
            (r"(?i)(?:user\s+input|human\s+input|provided\s+data|given\s+data)\s*:",
             "unmarked user input"),
            (r"(?i)(?:context|background|information)\s*:\s*$", "unbounded context"),
            (r"(?i)<\s*(?:user|human|input)\s*>.*?<\s*/\s*(?:user|human|input)\s*>",
             "xml user input tag"),
        ]

        for pattern, desc in boundary_patterns:
            for match in re.finditer(pattern, prompt, re.DOTALL):
                line_num = prompt[:match.start()].count("\n") + 1
                findings.append(Finding(
                    code=f"BOUNDARY_ISSUE_{desc.upper().replace(' ', '_')}",
                    severity=Severity.INFO,
                    message=f"Potential content boundary issue: {desc}",
                    evidence=match.group(0)[:100],
                    suggestion=(
                        "Clearly demarcate untrusted content with explicit boundaries "
                        "and instructions to not execute"
                    ),
                    location=(line_num, line_num),
                ))

        return findings


# Register
registry.register(SecurityAnalyzer())