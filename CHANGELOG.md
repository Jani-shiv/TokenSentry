# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-09

### Added
- **Core Engine**: Complete prompt analysis, optimization, and validation pipeline
- **7 Modular Analysis Engines**: Structure, Redundancy, Ambiguity, Contradictions, Complexity, Quality, Security
- **3 Optimization Profiles**: Conservative, Balanced, Aggressive with transformation tracking
- **Enhanced Validator**: Requirement preservation, literal verification, negative constraint weakening, schema validation, 7-status classification
- **Tokenizer Registry**: tiktoken (OpenAI), Hugging Face, SentencePiece adapters with exact/estimate metadata
- **15 AI Agent Skills**:
  - `tokensentry-analyzer`: Complete prompt analysis
  - `tokensentry-optimizer`: 3-profile optimization
  - `tokensentry-token-auditor`: Token consumption audit
  - `tokensentry-validator`: Requirement preservation validation
  - `tokensentry-context-engineer`: Context organization and prioritization
  - `tokensentry-system-prompt-designer`: System prompt design
  - `tokensentry-prompt-security-auditor`: Security audit (injection, secrets, unsafe)
  - `tokensentry-structured-output`: JSON/YAML/XML output optimization
  - `tokensentry-few-shot-optimizer`: Few-shot example optimization
  - `tokensentry-agent-workflow`: Multi-step agent workflow analysis
  - `tokensentry-model-adapter`: Cross-model tokenizer adaptation
  - `tokensentry-cost-analyst`: API cost estimation
  - `tokensentry-prompt-evaluator`: Quality scoring and test generation
  - `tokensentry-prompt-documenter`: Documentation generation
  - `tokensentry-skill-composer`: Multi-skill orchestration with dependency resolution
- **Skill Infrastructure**: Registry, loader, composer, validator with 3 predefined composition plans
- **Benchmark Framework**: 13 curated prompts across 7 categories, metrics, runner, JSON/Markdown reports
- **Report Exporters**: JSON, Markdown, and Rich terminal output
- **CLI**: analyze, optimize, validate, tokenizers, version commands with multiple output formats
- **Security**: Local-first processing, input validation, path safety, denied patterns, no telemetry

### Changed
- Refactored monolithic analyzer into 7 modular analysis engines
- Replaced simple optimizer with profile-based transformation registry
- Enhanced validator with 7-status change classification (exact/structural/probable/uncertain/modified/missing/weakened)
- Added JSON/YAML schema validation for structured output preservation

### Security
- Local-first processing (no network calls in core)
- Input validation with size limits and path safety
- Denied patterns for sensitive paths
- No hidden telemetry or prompt uploads
- Prompt content treated as untrusted data

## [0.0.1] - 2026-11-09

### Added
- Initial repository scaffold with CLI, models, core engines
- Basic analyzer, optimizer, validator
- Character-estimate tokenizer
- 5 skill metadata files
- GitHub Actions CI workflow
- Documentation (README, ARCHITECTURE, ROADMAP, CONTRIBUTING, SECURITY, SUPPORT, CODE_OF_CONDUCT)
- Apache-2.0 license