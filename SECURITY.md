# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅                 |
| < 0.1   | ❌                 |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email security@tokensentry.dev (or use GitHub's private vulnerability reporting)
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

We aim to:
- Acknowledge receipt within 48 hours
- Provide a fix timeline within 5 business days
- Release a patch within 30 days for critical vulnerabilities

## Security Best Practices

TokenSentry follows these security practices:

1. **Local-first processing**: No prompt data leaves your machine
2. **No telemetry**: No data collection without explicit consent
3. **Input validation**: All inputs validated and sanitized
4. **No code execution**: Prompts are analyzed, never executed
5. **Safe tokenizer handling**: Optional tokenizers loaded only when explicitly requested

## Reporting Channels

- **Email**: security@tokensentry.dev
- **GitHub**: [Private vulnerability reporting](https://github.com/Jani-shiv/TokenSentry/security/advisories/new)
- **PGP Key**: Available on request

## Scope

This policy covers:
- Core TokenSentry library (`tokensentry` package)
- Documentation site (`docs-site/`)
- CLI tool (`tokensentry` command)

Not covered:
- Third-party tokenizer libraries (tiktoken, tokenizers, sentencepiece)
- User-provided prompts (treated as untrusted input)
- Third-party integrations

## Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment and initial assessment
3. **Day 3-5**: Fix development begins
4. **Day 5-10**: Fix testing and validation
5. **Day 10-15**: Patch release preparation
6. **Day 15-30**: Public disclosure after patch release

## Recognition

We appreciate responsible disclosure. Contributors who report valid security issues will be acknowledged in:
- Release notes
- Security advisories
- Hall of Fame (with permission)