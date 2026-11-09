# Initial GitHub issues to create

Create these as separate issues after repository creation.

1. **Cross-platform CI for Python 3.11–3.13** (`ci`, `good first issue`): Ubuntu, Windows, macOS matrix; lint, type-check, tests; require green checks.
2. **Versioned JSON report schema** (`api`, `design`): schema version, tokenizer metadata, findings, transformations, validation warnings; fixtures and compatibility policy.
3. **Implement tiktoken adapter** (`tokenizers`, `good first issue`): explicit encoding selection, exactness metadata, no silent model guessing.
4. **Implement Hugging Face adapter** (`tokenizers`, `help wanted`): explicit model/local path, cache/offline behavior, no implicit runtime download.
5. **Implement SentencePiece adapter** (`tokenizers`, `help wanted`): local model support and deterministic tests.
6. **Structured prompt section parser** (`analyzer`, `enhancement`): headings, role-like sections, code fences, lists, schemas, source offsets.
7. **Protect technical literals** (`optimizer`, `safety`): preserve commands, paths, URLs, code, JSON/YAML and quoted literals byte-for-byte by default.
8. **Optimization profiles** (`optimizer`, `design`): conservative default plus balanced/aggressive modes and per-change trace.
9. **Requirement preservation validator** (`validator`, `research`): positive/negative constraints, exact values, output formats; distinguish deterministic from probabilistic checks.
10. **Validate Agent Skills metadata** (`skills`, `documentation`): check SKILL.md metadata against current specification and document platform compatibility.
11. **Markdown and JSON report exporters** (`reports`, `good first issue`): stable schema and tests.
12. **Optional LLM-assisted optimizer** (`integrations`, `privacy`): explicit opt-in, no default network calls, mocked tests, provider data disclosures.
13. **Benchmark corpus and evaluation harness** (`benchmarks`, `research`): documented provenance/licensing, reduction, retention, format, latency and failure metrics.
