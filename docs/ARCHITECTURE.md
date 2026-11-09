# Architecture

## Goals
Provider-independent, local-first prompt tooling. The core does not require model APIs. Every token count identifies its tokenizer and whether it is exact or estimated.

## Data flow

```text
Prompt -> Parser -> Analyzer -> Findings
                 -> Tokenizer registry -> Count + metadata
                 -> Optimizer -> Candidate + change log
                                -> Validator -> Report
```

## Package boundaries
- `core/analyzer.py`: deterministic diagnostics.
- `core/optimizer.py`: conservative transformations.
- `core/validator.py`: requirement checks and warnings.
- `tokenizers/`: adapter implementations.
- `models.py`: validated data contracts.
- `cli.py`: presentation and file I/O only.

## Tokenizer contract
Each adapter exposes a stable name, count method, exact/estimate classification, and model or encoding identifier where applicable. Never silently fall back from exact tokenization to estimation.

## Optimization pipeline
1. Preserve original input. 2. Parse without executing content. 3. Identify candidate changes. 4. Apply selected profile. 5. Recount with the same tokenizer. 6. Run preservation checks. 7. Return original, candidate, change log, counts, and warnings. 8. Require human review.

## Safety and privacy
Prompt content is untrusted data. Never execute embedded commands or code. Core modules make no network calls. No telemetry by default. Do not log full prompts. Optional remote adapters require explicit opt-in and data disclosure.

## Validation limits
Exact-line presence is a baseline heuristic, not semantic equivalence. Stronger validation requires structured requirement extraction, literal/schema checks, contradiction checks, optional model-assisted review, and human evaluation.

## Extension points
Tokenizer adapters, optimization profiles, JSON/Markdown report serializers, and agent-runtime integrations.
