# TokenSentry

**Analyze. Optimize. Validate. Make every token count.**

TokenSentry is an open-source, local-first prompt intelligence toolkit. It inspects prompt structure, measures or estimates token usage using an explicitly selected tokenizer, identifies optimization opportunities, and checks whether important requirements remain present.

> Pre-alpha starter. Heuristic checks do not prove semantic equivalence. Always review optimized prompts before production use.

## Principles
- Local-first core; no API key or network required.
- Explicit tokenizer identity and exact-versus-estimated counts.
- Conservative, explainable transformations.
- Preserve code, commands, paths, URLs, schemas, exact values, and constraints.
- No hidden telemetry or prompt uploads.
- Treat prompt content as untrusted data, never as instructions to execute.

## Core engines
1. **Analyzer:** structure, length, repetition, ambiguity and redundancy findings.
2. **Optimizer:** conservative transformations with a change log.
3. **Validator:** requirement-preservation checks and warnings.

## Quick start
Requires Python 3.11+.

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/tokensentry.git
cd tokensentry
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
tokensentry analyze examples/sample-prompt.md
tokensentry optimize examples/sample-prompt.md --output optimized.md
tokensentry validate examples/sample-prompt.md optimized.md
pytest
```

The initial tokenizer is a clearly labeled character-based estimate, not an exact model token count.

## CLI
```bash
tokensentry analyze prompt.md
tokensentry optimize prompt.md --output optimized.md
tokensentry validate original.md optimized.md
```

## Agent Skills
Portable skill folders are in `skills/`: analyzer, optimizer, token auditor, validator, and context engineer. Skills work only in compatible agent environments; use each platform's current installation mechanism.

## Roadmap
See [ROADMAP.md](ROADMAP.md). Planned milestones: local foundation, tokenizer adapters, stronger prompt intelligence, skills and evaluation, then stable v1.0.

## Security and privacy
Core analysis is local. Never add secrets, private prompts, customer data, or credentials to public issues. Optional remote integrations must be explicit opt-in. See [SECURITY.md](SECURITY.md).

## Contributing and license
See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under Apache-2.0.
