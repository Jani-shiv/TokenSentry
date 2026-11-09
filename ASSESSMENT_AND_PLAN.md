# TokenSentry Repository Assessment & Implementation Plan

**Date:** 2026-11-09  
**Auditor:** Nemotron 3 Ultra (Principal AI Engineer)  
**Repository:** https://github.com/Jani-shiv/TokenSentry  
**Local Path:** I:\Devops\Docker_Jani\tokensentry-starter\tokensentry

---

## A. Current Repository Assessment

### What Exists (Pre-Alpha Starter)

| Component | Status | Quality |
|-----------|--------|---------|
| **Package Structure** | ✅ Scaffolded | Clean `src/tokensentry/` layout |
| **Core Models** | ✅ Basic | Pydantic v2, minimal fields |
| **Analyzer Engine** | 🟡 Starter | Repeated-line detection + stats only |
| **Optimizer Engine** | 🟡 Starter | Whitespace normalization only |
| **Validator Engine** | 🟡 Starter | Exact-line presence heuristic |
| **Tokenizer System** | 🟡 Starter | Character-estimate only (labeled as estimate) |
| **CLI** | ✅ Functional | `analyze`, `optimize`, `validate` commands |
| **Tests** | 🟡 Minimal | 4 basic tests covering core functions |
| **CI/CD** | ✅ Configured | 3 OS × 3 Python versions matrix |
| **Skills (5/15)** | 🟡 Starter | Metadata only, no implementation |
| **Documentation** | ✅ Good | README, ARCHITECTURE, ROADMAP, CONTRIBUTING, SECURITY, etc. |
| **License** | ✅ Apache-2.0 | Properly attributed |
| **Issue Templates** | ✅ Present | Bug report, feature request |
| **Project Config** | ✅ pyproject.toml | Hatchling, Ruff, MyPy, Pytest configured |

### What's Missing (Per Master Development Prompt)

| Category | Missing Components |
|----------|-------------------|
| **Tokenizer Adapters** | tiktoken, Hugging Face, SentencePiece (3 adapters) |
| **Analyzer Capabilities** | Section parser, constraint extraction, ambiguity/contradiction detection, security analysis, quality scoring |
| **Optimization Profiles** | Conservative (beyond whitespace), Balanced, Aggressive with change tracking |
| **Validator** | Requirement extraction, negative constraint checking, technical literal preservation, schema validation |
| **Skills (10/15)** | system-prompt-designer, prompt-security-auditor, structured-output, few-shot-optimizer, agent-workflow, model-adapter, cost-analyst, prompt-evaluator, prompt-documenter, skill-composer |
| **Skill Infrastructure** | Registry, loader, validator, composer |
| **Reports** | JSON, Markdown, Terminal exporters with stable schemas |
| **Benchmarks** | Corpus, metrics, runner, evaluation harness |
| **API Layer** | FastAPI schemas, REST endpoints (future) |
| **Context Engine** | Context organization, prioritization, compression |
| **Security Hardening** | Input validation, size limits, path traversal protection |

---

## B. Existing vs Missing Components Matrix

### Core Engines (7 required)

| Engine | File | Status | Gap |
|--------|------|--------|-----|
| Analyzer | `core/analyzer.py` | 10% | 90% - needs structure parsing, ambiguity, contradictions, security, quality |
| Tokenizer | `tokenizers/` | 10% | 90% - needs 3 real adapters + registry |
| Optimizer | `core/optimizer.py` | 5% | 95% - needs 3 profiles, transformations, preservation |
| Validator | `core/validator.py` | 5% | 95% - needs requirement extraction, literal preservation |
| Skills | `skills/` | 20% | 80% - 5/15 skills, no registry/composer |
| Benchmarks | `benchmarks/` | 0% | 100% - entirely missing |
| Reports | `reports/` | 0% | 100% - entirely missing |

### Skills Catalog (15 required)

| # | Skill | Directory | Status |
|---|-------|-----------|--------|
| 01 | tokensentry-analyzer | ✅ exists | Metadata only |
| 02 | tokensentry-optimizer | ✅ exists | Metadata only |
| 03 | tokensentry-token-auditor | ✅ exists | Metadata only |
| 04 | tokensentry-validator | ✅ exists | Metadata only |
| 05 | tokensentry-context-engineer | ✅ exists | Metadata only |
| 06 | tokensentry-system-prompt-designer | ❌ missing | Not created |
| 07 | tokensentry-prompt-security-auditor | ❌ missing | Not created |
| 08 | tokensentry-structured-output | ❌ missing | Not created |
| 09 | tokensentry-few-shot-optimizer | ❌ missing | Not created |
| 10 | tokensentry-agent-workflow | ❌ missing | Not created |
| 11 | tokensentry-model-adapter | ❌ missing | Not created |
| 12 | tokensentry-cost-analyst | ❌ missing | Not created |
| 13 | tokensentry-prompt-evaluator | ❌ missing | Not created |
| 14 | tokensentry-prompt-documenter | ❌ missing | Not created |
| 15 | tokensentry-skill-composer | ❌ missing | Not created |

---

## C. Recommended Final Architecture

### Package Structure (Target)

```
src/tokensentry/
├── __init__.py
├── models.py                    # Extended with all data contracts
├── config.py                    # Configuration management
├── cli.py                       # Extended CLI with all commands
│
├── core/
│   ├── __init__.py
│   ├── analyzer.py              # Full prompt intelligence
│   ├── optimizer.py             # 3-profile optimizer
│   ├── validator.py             # Semantic validation
│   ├── context_engine.py        # Context organization
│   └── requirements.py          # Requirement extraction
│
├── tokenizers/
│   ├── __init__.py
│   ├── base.py                  # Abstract base + registry
│   ├── registry.py              # Tokenizer registry
│   ├── tiktoken_adapter.py      # OpenAI tiktoken
│   ├── huggingface_adapter.py   # HF tokenizers
│   ├── sentencepiece_adapter.py # SentencePiece
│   └── approximate.py           # Existing estimate
│
├── skills/
│   ├── __init__.py
│   ├── registry.py              # Skill registry
│   ├── loader.py                # Skill loading
│   ├── validator.py             # Skill metadata validation
│   └── composer.py              # Skill orchestration
│
├── analysis/
│   ├── __init__.py
│   ├── structure.py             # Section parsing
│   ├── redundancy.py            # Duplicate detection
│   ├── ambiguity.py             # Ambiguity heuristics
│   ├── contradictions.py        # Conflict detection
│   ├── complexity.py            # Complexity metrics
│   ├── quality.py               # Quality scoring
│   └── security.py              # Security analysis
│
├── optimization/
│   ├── __init__.py
│   ├── conservative.py          # Conservative profile
│   ├── balanced.py              # Balanced profile
│   ├── aggressive.py            # Aggressive profile
│   ├── transformations.py       # Transformation primitives
│   └── preservation.py          # Literal preservation
│
├── benchmarks/
│   ├── __init__.py
│   ├── datasets.py              # Benchmark corpora
│   ├── metrics.py               # Evaluation metrics
│   ├── runner.py                # Benchmark execution
│   └── reports.py               # Benchmark reporting
│
├── reports/
│   ├── __init__.py
│   ├── json.py                  # JSON export
│   ├── markdown.py              # Markdown export
│   └── terminal.py              # Rich terminal output
│
├── api/
│   ├── __init__.py
│   └── schemas.py               # FastAPI/OpenAPI schemas
```

---

## D. Dependency Assessment

### Current Dependencies (pyproject.toml)

```toml
dependencies = [
    "typer>=0.12,<1.0",      # CLI ✅
    "rich>=13.7,<15",        # Terminal output ✅
    "pydantic>=2.7,<3",      # Data validation ✅
]

optional-dependencies:
  dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.5", "mypy>=1.10"]
  openai-tokenizer = ["tiktoken>=0.7"]
  huggingface-tokenizer = ["tokenizers>=0.19"]
  sentencepiece = ["sentencepiece>=0.2"]
```

### Required Additional Dependencies

| Dependency | Purpose | Justification |
|------------|---------|---------------|
| `pyyaml` | YAML parsing for prompts/schemas | Standard library alternative insufficient |
| `jsonschema` | JSON schema validation | Required for structured-output skill |
| `rapidfuzz` | Fuzzy matching for deduplication | Better than difflib for prompt similarity |
| `textstat` | Readability metrics | Quality scoring |
| `sentencepiece` | Optional tokenizer | Already in optional-deps |
| `tiktoken` | OpenAI tokenizer | Already in optional-deps |
| `tokenizers` | HF tokenizer | Already in optional-deps |
| `fastapi` `uvicorn` | Optional API server | Future integration, keep optional |

### Decision: Keep Core Minimal
- Add `pyyaml` and `jsonschema` to core (small, well-maintained)
- Keep `rapidfuzz`, `textstat` as optional for quality features
- All tokenizer libraries remain optional extras

---

## E. Security Assessment

### Current Security Posture

| Check | Status | Notes |
|-------|--------|-------|
| Local-first processing | ✅ | No network calls in core |
| No telemetry | ✅ | No analytics |
| No prompt uploads | ✅ | By design |
| Input validation | 🟡 | Basic only, needs hardening |
| Size limits | ❌ | No max input size |
| Path traversal | ❌ | CLI reads arbitrary files |
| Secret exposure | ✅ | Not in code |
| Skill metadata validation | ❌ | Not implemented |
| Untrusted content handling | 🟡 | Documented but not enforced |

### Required Security Hardening

1. **Input size limits** - Max 10MB prompts, configurable
2. **Path validation** - Restrict file reads to safe directories
3. **Skill metadata validation** - Schema validation on load
4. **Prompt sanitization** - Strip null bytes, control chars
5. **Timeout guards** - Prevent infinite loops on pathological input
6. **Memory limits** - Streaming for large prompts

---

## F. Skills Implementation Plan

### Phase 1: Skill Infrastructure (Weeks 1-2)
- [ ] Skill base class and protocol
- [ ] Skill registry with discovery
- [ ] Skill metadata validator (JSON Schema)
- [ ] Skill loader with dependency resolution
- [ ] Skill composer with DAG execution

### Phase 2: Core 5 Skills Implementation (Weeks 2-4)
Each skill gets:
- [ ] Implementation module
- [ ] SKILL.md metadata
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation

| Skill | Priority | Est. Effort |
|-------|----------|-------------|
| tokensentry-analyzer | P0 | 3 days |
| tokensentry-optimizer | P0 | 4 days |
| tokensentry-token-auditor | P0 | 2 days |
| tokensentry-validator | P0 | 3 days |
| tokensentry-context-engineer | P0 | 3 days |

### Phase 3: Remaining 10 Skills (Weeks 4-8)
| Skill | Priority | Est. Effort | Dependencies |
|-------|----------|-------------|--------------|
| tokensentry-system-prompt-designer | P1 | 2 days | analyzer |
| tokensentry-prompt-security-auditor | P1 | 2 days | analyzer |
| tokensentry-structured-output | P1 | 2 days | validator |
| tokensentry-few-shot-optimizer | P1 | 2 days | analyzer |
| tokensentry-agent-workflow | P1 | 3 days | analyzer, validator |
| tokensentry-model-adapter | P1 | 2 days | tokenizers |
| tokensentry-cost-analyst | P2 | 2 days | token-auditor |
| tokensentry-prompt-evaluator | P2 | 3 days | analyzer, validator |
| tokensentry-prompt-documenter | P2 | 2 days | analyzer |
| tokensentry-skill-composer | P0 | 3 days | skill infrastructure |

---

## G. Phased Development Plan (10 Phases)

### PHASE 1: Repository Audit & Planning ✅ COMPLETE
**Deliverable:** This document

### PHASE 2: Stable Python Core & Data Models (Week 1)
**Goal:** Extend models, add config, harden CLI

| Task | Owner | Tests |
|------|-------|-------|
| Extend `models.py` with all data contracts | Core | Unit |
| Add `config.py` with Pydantic Settings | Core | Unit |
| Harden CLI: size limits, path validation, timeouts | Core | Integration |
| Add JSON/Markdown report exporters | Reports | Unit |
| Run: `ruff`, `mypy`, `pytest` | All | CI |

**Definition of Done:** All tests pass, type-check clean, CLI handles edge cases

### PHASE 3: Tokenizer Adapters & Measurement (Week 1-2)
**Goal:** Three production tokenizer adapters + registry

| Task | Owner | Tests |
|------|-------|-------|
| Create `tokenizers/base.py` abstract base | Tokenizers | Unit |
| Create `tokenizers/registry.py` with discovery | Tokenizers | Unit |
| Implement `tiktoken_adapter.py` | Tokenizers | Unit + Fixtures |
| Implement `huggingface_adapter.py` | Tokenizers | Unit + Fixtures |
| Implement `sentencepiece_adapter.py` | Tokenizers | Unit + Fixtures |
| Update CLI to accept `--tokenizer` flag | CLI | Integration |
| Document exactness metadata requirements | Docs | - |

**Definition of Done:** All 3 adapters work, exact/estimate labeled correctly, no silent fallbacks

### PHASE 4: Analyzer Capabilities (Week 2-3)
**Goal:** Full prompt intelligence

| Module | Capabilities |
|--------|--------------|
| `analysis/structure.py` | Section parser (headings, code fences, lists, schemas), source offsets |
| `analysis/redundancy.py` | Duplicate detection (lines, phrases, semantic similarity) |
| `analysis/ambiguity.py` | Vague language, underspecified constraints, missing context |
| `analysis/contradictions.py` | Conflicting instructions, incompatible constraints |
| `analysis/complexity.py` | Cyclomatic-like metrics, nesting depth, token density |
| `analysis/quality.py` | Clarity, completeness, actionability scores |
| `analysis/security.py` | Injection patterns, secret exposure, unsafe instructions |

**Integration:** Update `core/analyzer.py` to orchestrate all analyzers

### PHASE 5: Optimization Profiles (Week 3-4)
**Goal:** Three optimization modes with preservation

| Profile | Transformations |
|---------|-----------------|
| Conservative | Whitespace, exact duplicate removal, formatting |
| Balanced | + Consolidate redundant instructions, improve sentence structure, deduplicate examples |
| Aggressive | + Reorganize sections, compress context, propose low-value removals (with warnings) |

| Module | Responsibility |
|--------|----------------|
| `optimization/transformations.py` | Atomic transformations with reversibility |
| `optimization/preservation.py` | Literal protection (code, commands, URLs, schemas, values) |
| `optimization/conservative.py` | Profile implementation |
| `optimization/balanced.py` | Profile implementation |
| `optimization/aggressive.py` | Profile implementation |

**Integration:** Update `core/optimizer.py` with profile selection

### PHASE 6: Validation & Preservation (Week 4-5)
**Goal:** Semantic preservation validation

| Capability | Implementation |
|------------|----------------|
| Requirement extraction | Parse explicit must/must-not/should constraints |
| Negative constraint checking | Verify prohibitions preserved |
| Technical literal preservation | Byte-for-byte code/command/URL/schema protection |
| Output schema validation | JSON/YAML structure preservation |
| Change classification | Exact/Structural/Probable/Uncertain/Missing |

**Output:** Detailed validation report with evidence

### PHASE 7: All 15 Skills Implementation (Week 5-8)
**Goal:** Complete skill catalog

See Section F for detailed breakdown. Each skill delivers:
- Implementation module in `skills/<name>/`
- SKILL.md with metadata
- Tests in `tests/skills/test_<name>.py`
- Example usage in `examples/skills/<name>/`

### PHASE 8: Skill Registry & Composition (Week 8-9)
**Goal:** Orchestration system

| Component | Function |
|-----------|----------|
| `skills/registry.py` | Discovery, registration, versioning |
| `skills/loader.py` | Load with dependency resolution |
| `skills/validator.py` | SKILL.md schema validation |
| `skills/composer.py` | DAG execution, result passing, conflict resolution |

**CLI:** `tokensentry skill list`, `tokensentry skill run <name>`, `tokensentry workflow run <config>`

### PHASE 9: Benchmarks, Reports & Documentation (Week 9-10)
**Goal:** Evaluation and polish

| Deliverable | Description |
|-------------|-------------|
| `benchmarks/datasets.py` | Curated prompts with licenses |
| `benchmarks/metrics.py` | Token reduction, retention, latency, quality |
| `benchmarks/runner.py` | Automated evaluation harness |
| `reports/json.py` | Stable JSON schema v1 |
| `reports/markdown.py` | Human-readable reports |
| `reports/terminal.py` | Rich CLI output |
| Documentation | All 15 skills, API, architecture, contributing |

### PHASE 10: CI/CD, Release Prep & GitHub Sync (Week 10)
**Goal:** Production readiness

| Task | Status |
|------|--------|
| Cross-platform CI passing | Required |
| Security scan (bandit, pip-audit) | Required |
| Dependency review | Required |
| Version bump to 0.1.0 | Required |
| CHANGELOG finalized | Required |
| GitHub release tagged | Required |
| Push to origin/main | Required |

---

## H. Initial Prioritized GitHub Issues

### P0 - Critical Path (Must Complete First)

| # | Title | Labels | Effort |
|---|-------|--------|--------|
| 1 | Implement tiktoken adapter with exactness metadata | `tokenizers`, `good first issue` | 2 days |
| 2 | Implement Hugging Face tokenizer adapter | `tokenizers`, `help wanted` | 2 days |
| 3 | Implement SentencePiece adapter | `tokenizers`, `help wanted` | 2 days |
| 4 | Create tokenizer registry and base class | `tokenizers`, `architecture` | 1 day |
| 5 | Extend data models for full analysis/optimization/validation | `core`, `api` | 2 days |
| 6 | Add input validation, size limits, path safety to CLI | `security`, `cli` | 1 day |
| 7 | Implement prompt section parser (headings, code fences, lists) | `analyzer`, `enhancement` | 3 days |
| 8 | Implement requirement extraction (must/must-not/values) | `analyzer`, `validator` | 3 days |
| 9 | Implement technical literal preservation (code, URLs, schemas) | `optimizer`, `safety` | 3 days |
| 10 | Create optimization profiles: conservative, balanced, aggressive | `optimizer`, `design` | 4 days |

### P1 - High Priority (Core Features)

| # | Title | Labels | Effort |
|---|-------|--------|--------|
| 11 | Implement redundancy detection (semantic + exact) | `analyzer` | 2 days |
| 12 | Implement ambiguity and contradiction heuristics | `analyzer` | 2 days |
| 13 | Implement security analysis (injection, secrets, unsafe tools) | `analyzer`, `security` | 2 days |
| 14 | Implement quality scoring (clarity, completeness, actionability) | `analyzer` | 2 days |
| 15 | Build requirement preservation validator | `validator`, `research` | 3 days |
| 16 | Implement context engine (organization, prioritization, compression) | `core`, `enhancement` | 3 days |
| 17 | Create JSON and Markdown report exporters with stable schema | `reports`, `good first issue` | 2 days |
| 18 | Build skill infrastructure (registry, loader, validator, composer) | `skills`, `architecture` | 3 days |

### P2 - Skills Implementation (15 Skills)

| # | Title | Labels | Effort |
|---|-------|--------|--------|
| 19 | Implement tokensentry-analyzer skill | `skills`, `analyzer` | 2 days |
| 20 | Implement tokensentry-optimizer skill | `skills`, `optimizer` | 2 days |
| 21 | Implement tokensentry-token-auditor skill | `skills`, `tokenizers` | 1 day |
| 22 | Implement tokensentry-validator skill | `skills`, `validator` | 2 days |
| 23 | Implement tokensentry-context-engineer skill | `skills`, `core` | 2 days |
| 24 | Implement tokensentry-system-prompt-designer skill | `skills`, `enhancement` | 2 days |
| 25 | Implement tokensentry-prompt-security-auditor skill | `skills`, `security` | 2 days |
| 26 | Implement tokensentry-structured-output skill | `skills`, `validator` | 2 days |
| 27 | Implement tokensentry-few-shot-optimizer skill | `skills`, `analyzer` | 2 days |
| 28 | Implement tokensentry-agent-workflow skill | `skills`, `enhancement` | 3 days |
| 29 | Implement tokensentry-model-adapter skill | `skills`, `tokenizers` | 2 days |
| 30 | Implement tokensentry-cost-analyst skill | `skills`, `token-auditor` | 2 days |
| 31 | Implement tokensentry-prompt-evaluator skill | `skills`, `evaluation` | 3 days |
| 32 | Implement tokensentry-prompt-documenter skill | `skills`, `documentation` | 2 days |
| 33 | Implement tokensentry-skill-composer skill | `skills`, `architecture` | 3 days |

### P3 - Evaluation & Polish

| # | Title | Labels | Effort |
|---|-------|--------|--------|
| 34 | Create benchmark corpus with documented licenses | `benchmarks`, `research` | 3 days |
| 35 | Build evaluation harness (reduction, retention, quality) | `benchmarks`, `research` | 3 days |
| 36 | Add optional FastAPI server with OpenAPI schemas | `api`, `future` | 2 days |
| 37 | Complete documentation for all skills and APIs | `documentation` | 3 days |
| 38 | Security review and penetration testing | `security` | 2 days |
| 39 | Cross-platform testing and release automation | `ci`, `release` | 2 days |

---

## Next Steps

1. **Review this plan** - Confirm priorities and scope
2. **Authorize Phase 2** - Begin core model extensions and CLI hardening
3. **Create GitHub issues** - Convert the above into trackable issues
4. **Set up project board** - Organize by phase and priority
5. **Begin implementation** - Work in phases with reviews at each gate

---

**Estimated Timeline:** 10-12 weeks for v0.1.0 stable release  
**Team Size:** 1-2 engineers (can parallelize tokenizer adapters, skills)  
**Risk Areas:** Semantic validation accuracy, skill composition complexity, benchmark corpus licensing