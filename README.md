# TokenSentry — AI Skill Integration Guide

> **Use TokenSentry as a skill in your AI applications** — Analyze, optimize, and validate prompts programmatically with 15 specialized AI agent skills.

---

## 🚀 Quick Start

```bash
# Install with all skills
pip install "tokensentry[all]"

# Or install specific components
pip install "tokensentry[openai-tokenizer]"      # OpenAI models (GPT-4, GPT-4o, etc.)
pip install "tokensentry[huggingface-tokenizer]"  # Llama, Mistral, Gemma, etc.
pip install "tokensentry[sentencepiece]"          # Custom SentencePiece models
```

---

## 🎯 Using TokenSentry as an AI Skill

TokenSentry provides **15 specialized AI agent skills** that can be composed into workflows. Each skill is a self-contained module with well-defined inputs/outputs.

### Quick Example: Analyze → Optimize → Validate

```python
from tokensentry import analyze_prompt, optimize_prompt, validate_prompt
from tokensentry.skills import registry

# 1. ANALYZE — Deep prompt analysis
prompt = """
Act as a senior Python developer.
Review this code for performance issues and security vulnerabilities.

```python
def process_user_data(users):
    results = []
    for user in users:
        query = f"SELECT * FROM users WHERE id = {user.id}"
        results.append(db.execute(query))
    return results
```

Identify: SQL injection, N+1 queries, missing validation.
Provide fixed code with explanations.
"""

analysis = analyze_prompt(prompt, tokenizer="tiktoken:gpt-4")
print(f"Tokens: {analysis.token_count}")
print(f"Findings: {len(analysis.findings)}")
print(f"Quality: {analysis.quality_scores['overall']:.2f}")

# 2. OPTIMIZE — Reduce tokens while preserving intent
optimization = optimize_prompt(
    prompt,
    profile="balanced",          # conservative | balanced | aggressive
    tokenizer="tiktoken:gpt-4"
)
print(f"Token reduction: {optimization.token_delta} ({optimization.token_reduction_pct:.1f}%)")
print(f"Transformations: {len(optimization.transformations)}")

# 3. VALIDATE — Ensure nothing critical was lost
validation = validate_prompt(prompt, optimization.optimized)
print(f"Passed: {validation.passed}")
print(f"Preserved: {len(validation.preserved_lines)}")
print(f"Missing: {len(validation.missing_lines)}")
print(f"Weakened: {len(validation.weakened_negatives)}")
```

---

## 🧩 Using Individual Skills

Each skill is independently usable. Import and run them directly:

### Analyzer Skill
```python
from tokensentry.skills.analyzer import AnalyzerSkill
from tokensentry.skills.base import SkillContext

skill = AnalyzerSkill()
context = SkillContext(prompt="Your prompt here...")
result = skill.execute(context)

# Access structured analysis
print(f"Tokens: {result.output.token_count}")
print(f"Requirements: {len(result.output.requirements)}")
print(f"Security findings: {len([f for f in result.output.findings if 'SECURITY' in f.code])}")
```

### Optimizer Skill
```python
from tokensentry.skills.optimizer import OptimizerSkill
from tokensentry.models import OptimizationProfile

skill = OptimizerSkill()
context = SkillContext(prompt="Your long prompt here...")
result = skill.execute(context, config={
    "profile": "balanced",  # conservative | balanced | aggressive
    "tokenizer": "tiktoken:gpt-4"
})

print(f"Token reduction: {result.output.token_reduction_pct:.1f}%")
print(f"Warnings: {result.output.warnings}")
```

### Validator Skill
```python
from tokensentry.skills.validator import ValidatorSkill

skill = ValidatorSkill()
context = SkillContext(
    prompt="Original prompt...",
    metadata={"original_prompt": "Original prompt...", "optimized_prompt": "Optimized prompt..."}
)
result = skill.execute(context)

print(f"Passed: {result.output.passed}")
print(f"Missing: {result.output.missing_lines}")
print(f"Weakened: {result.output.weakened_negatives}")
```

### Security Auditor Skill
```python
from tokensentry.skills.security_auditor import PromptSecurityAuditorSkill

skill = PromptSecurityAuditorSkill()
context = SkillContext(prompt="User input here...")
result = skill.execute(context, config={"strict_mode": True})

print(f"Risk level: {result.output.risk_level}")
for finding in result.output.findings:
    print(f"  {finding.code}: {finding.message}")
```

### Cost Analyst Skill
```python
from tokensentry.skills.cost_analyst import CostAnalystSkill

skill = CostAnalystSkill()
context = SkillContext(prompt="Your prompt...")
result = skill.execute(context, config={
    "models": ["gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet"],
    "output_tokens_estimate": 500,
    "requests_per_month": 10000
})

for model, cost in result.output["monthly_cost_estimate"].items():
    print(f"{model}: ${cost['estimated_monthly_usd']:.2f}/month")
```

---

## 🔗 Composing Skills into Workflows

Use the **Skill Composer** to orchestrate multiple skills with dependency resolution:

```python
from tokensentry.skills import registry
from tokensentry.skills.composer import SkillComposer, CompositionPlan, CompositionStep
from tokensentry.skills.base import SkillContext

composer = SkillComposer(registry)

# Use predefined plans
plan = registry.get_plan("full")  # standard | full | security

# Or create custom composition
custom_plan = CompositionPlan(
    name="custom-analysis",
    steps=[
        CompositionStep(skill_name="tokensentry-analyzer"),
        CompositionStep(skill_name="tokensentry-token-auditor", depends_on=["tokensentry-analyzer"]),
        CompositionStep(skill_name="tokensentry-optimizer", depends_on=["tokensentry-analyzer", "tokensentry-token-auditor"]),
        CompositionStep(skill_name="tokensentry-validator", depends_on=["tokensentry-optimizer"]),
    ]
)

context = SkillContext(prompt="Your prompt here...")
results = composer.execute_plan(custom_plan, context)

# Access all results
for skill_name, result in results.items():
    if result.success:
        print(f"✅ {skill_name}: {result.output}")
    else:
        print(f"❌ {skill_name}: {result.error}")
```

### Predefined Plans

| Plan | Steps | Use Case |
|------|-------|----------|
| `standard` | analyzer → token-auditor → security-auditor | General analysis |
| `full` | analyzer → token-auditor → optimizer → validator | Full optimization pipeline |
| `security` | analyzer → security-auditor → prompt-security-auditor | Security-focused |

---

## 🔧 Configuration

### Environment Variables
```bash
# Core settings
export TOKENSENTRY_MAX_PROMPT_SIZE=10485760      # 10MB max prompt
TOKENSENTRY_DEFAULT_TOKENIZER=character-estimate
TOKENSENTRY_DEFAULT_PROFILE=conservative
TOKENSENTRY_ENABLE_SECURITY_CHECKS=true
TOKENSENTRY_TIMEOUT_SECONDS=30

# Tokenizer caches
TOKENSENTRY_TIKTOKEN_CACHE_DIR=/path/to/cache
TOKENSENTRY_HF_CACHE_DIR=/path/to/hf/cache
TOKENSENTRY_HF_OFFLINE_MODE=false
```

### Configuration File (`.tokensentry.yaml`)
```yaml
default_tokenizer: "tiktoken:gpt-4"
default_optimization_profile: "balanced"
enable_security_checks: true
enable_quality_scoring: true
timeout_seconds: 60

max_prompt_size: 10485760
max_line_length: 10000

denied_patterns:
  - ".."
  - "~"
  - "secret"
  - "password"
  - "api_key"

allowed_read_paths:
  - "./prompts"
  - "./examples"

skills:
  auto_load: true
  directories:
    - "./custom-skills"
  default_skills:
    - "tokensentry-analyzer"
    - "tokensentry-optimizer"
    - "tokensentry-validator"

benchmarks:
  corpus_path: "./benchmarks/corpus"
  results_path: "./benchmarks/results"
  default_profiles: ["conservative", "balanced", "aggressive"]
  categories: ["software_engineering", "devops", "security"]
```

---

## 🤖 Using TokenSentry in AI Applications

### As a LangChain Tool
```python
from langchain.tools import Tool
from tokensentry import analyze_prompt, optimize_prompt, validate_prompt

analyze_tool = Tool(
    name="analyze_prompt",
    func=lambda prompt: analyze_prompt(prompt).model_dump_json(),
    description="Analyze prompt structure, quality, and tokens"
)

optimize_tool = Tool(
    name="optimize_prompt",
    func=lambda prompt, profile="balanced": optimize_prompt(prompt, profile=profile).model_dump_json(),
    description="Optimize prompt with specified profile"
)

validate_tool = Tool(
    name="validate_prompt",
    func=lambda original, optimized: validate_prompt(original, optimized).model_dump_json(),
    description="Validate optimized prompt against original"
)

# Use in LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

agent = initialize_agent(
    tools=[analyze_tool, optimize_tool, validate_tool],
    llm=OpenAI(temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("Analyze and optimize this prompt: 'Write a Python function...'")
```

### As a FastAPI Service
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokensentry import analyze_prompt, optimize_prompt, validate_prompt

app = FastAPI(title="TokenSentry API")

class AnalyzeRequest(BaseModel):
    prompt: str
    tokenizer: str = "character-estimate"

class OptimizeRequest(BaseModel):
    prompt: str
    profile: str = "balanced"
    tokenizer: str = "character-estimate"

class ValidateRequest(BaseModel):
    original: str
    optimized: str
    tokenizer: str = "character-estimate"

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    return analyze_prompt(req.prompt, tokenizer_name=req.tokenizer)

@app.post("/optimize")
async def optimize(req: OptimizeRequest):
    return optimize_prompt(req.prompt, profile=req.profile, tokenizer_name=req.tokenizer)

@app.post("/validate")
async def validate(req: ValidateRequest):
    return validate_prompt(req.original, req.optimized, tokenizer_name=req.tokenizer)
```

---

## 🧪 Running Benchmarks

```bash
# Run all benchmarks
tokensentry benchmark run

# Specific profiles
tokensentry benchmark run --profiles conservative balanced

# Limit prompts for quick test
tokensentry benchmark run --max-prompts 5 --categories software_engineering

# Save results
tokensentry benchmark run --output results.json

# Generate reports
tokensentry benchmark report results.json --format markdown
tokensentry benchmark report results.json --format json
```

---

## 🔧 Extending TokenSentry

### Custom Skill
```python
from tokensentry.skills.base import BaseSkill, SkillContext, SkillResult
from tokensentry.models import SkillMetadata

class MyCustomSkill(BaseSkill):
    metadata = SkillMetadata(
        name="tokensentry-my-skill",
        version="1.0.0",
        description="My custom analysis skill",
        capabilities=["custom-analysis"],
        input_schema={"type": "object", "properties": {"prompt": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        dependencies=["tokensentry-analyzer"],
        tags=["custom", "analysis"],
        entry_point="my_skill.py",
        min_tokensentry_version="0.1.0"
    )

    def execute(self, context: SkillContext) -> SkillResult:
        # Your custom logic here
        result = {"analysis": "custom result"}
        return SkillResult(
            skill_name=self.metadata.name,
            success=True,
            output=result
        )

# Register
from tokensentry.skills import registry
registry.register(MyCustomSkill)
```

### Custom Tokenizer
```python
from tokensentry.tokenizers.registry import BaseTokenizer, register_tokenizer
from tokensentry.models import TokenCountKind

class MyCustomTokenizer(BaseTokenizer):
    name = "my-custom-tokenizer"
    version = "1.0"
    count_kind = TokenCountKind.EXACT
    model_id = "my-model"
    encoding = "custom"

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._tokenizer = None

    def _load(self):
        # Load your tokenizer
        pass

    def count(self, text: str) -> int:
        if not text:
            return 0
        return len(self._load().encode(text))

# Register
register_tokenizer("custom:my-tokenizer", lambda: MyCustomTokenizer("/path/to/model"))
```

---

## 📚 API Reference

### Core Functions
| Function | Description |
|----------|-------------|
| `analyze_prompt(prompt, tokenizer, prompt_id)` | Full prompt analysis |
| `optimize_prompt(prompt, profile, tokenizer, literals)` | Optimize with profile |
| `validate_prompt(original, optimized, requirements, literals)` | Validate preservation |

### Skill Registry
| Method | Description |
|--------|-------------|
| `registry.list_skills()` | List all registered skills |
| `registry.get(name)` | Get skill class by name |
| `registry.get_instance(name, config)` | Get instantiated skill |
| `registry.register(skill_class)` | Register new skill |

### Models
| Model | Purpose |
|-------|---------|
| `AnalysisReport` | Complete analysis results |
| `OptimizationResult` | Optimization with transformations |
| `ValidationReport` | Validation with 7-status checks |
| `SkillMetadata` | Skill metadata & schemas |
| `SkillContext` | Input context for skills |
| `SkillResult` | Skill execution result |

---

## 📚 Resources

- **Documentation**: https://tokensentry.dev
- **GitHub**: https://github.com/Jani-shiv/TokenSentry
- **PyPI**: https://pypi.org/project/tokensentry
- **Issues**: https://github.com/Jani-shiv/TokenSentry/issues
- **Discussions**: https://github.com/Jani-shiv/TokenSentry/discussions

---

## 📄 License

Apache-2.0 — See [LICENSE](LICENSE) for details.

---

*TokenSentry v0.1.1 — Analyze. Optimize. Validate. Make every token count.*