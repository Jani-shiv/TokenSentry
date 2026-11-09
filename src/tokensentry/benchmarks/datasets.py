"""Benchmark datasets for TokenSentry evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkPrompt:
    """A single benchmark prompt with metadata."""

    id: str
    name: str
    prompt: str
    category: str
    difficulty: str  # easy, medium, hard
    expected_tokens: int | None = None
    license: str = "MIT"
    source: str = "tokensentry"
    tags: list[str] = None
    reference_output: str | None = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


# Core benchmark prompts
BENCHMARK_PROMPTS: list[BenchmarkPrompt] = [
    # Software Engineering
    BenchmarkPrompt(
        id="se_001",
        name="Kubernetes Explanation",
        category="software_engineering",
        difficulty="medium",
        prompt="""Act as a senior DevOps engineer.

Explain Kubernetes for a beginner using clear English. Cover its purpose, architecture, control plane, worker nodes, core components, and how a request reaches a running container.

Include practical kubectl commands and explain what each command does. Do not assume production experience. Use headings and finish with a short recap.""",
        expected_tokens=400,
        tags=["kubernetes", "devops", "explanation"],
    ),

    BenchmarkPrompt(
        id="se_002",
        name="REST API Design",
        category="software_engineering",
        difficulty="medium",
        prompt="""Design a RESTful API for a task management system. The API should support:

1. CRUD operations for tasks (title, description, status, priority, due_date, assignee)
2. Filtering by status, priority, assignee
3. Pagination for list endpoints
4. Proper HTTP status codes
5. Request/response examples in JSON
6. Error handling with consistent format
7. Authentication via Bearer tokens
8. Rate limiting considerations

Provide OpenAPI 3.0 specification in YAML format.""",
        expected_tokens=800,
        tags=["api", "rest", "openapi", "design"],
    ),

    BenchmarkPrompt(
        id="se_003",
        name="Database Migration Script",
        category="software_engineering",
        difficulty="hard",
        prompt="""Write a PostgreSQL migration script to:

1. Create a new table `user_profiles` with columns: id (UUID, PK), user_id (FK to users), bio (TEXT), avatar_url (VARCHAR), preferences (JSONB), created_at, updated_at
2. Add index on user_id
3. Add trigger to auto-update updated_at
4. Migrate existing data from `users.profile_data` JSONB column
5. Handle rollback scenario
5. Use transactions for safety

Provide both up and down migrations in SQL.""",
        expected_tokens=600,
        tags=["database", "postgresql", "migration", "sql"],
    ),

    # DevOps / Infrastructure
    BenchmarkPrompt(
        id="devops_001",
        name="Terraform AWS Infrastructure",
        category="devops",
        difficulty="hard",
        prompt="""Create a Terraform configuration for AWS infrastructure:

1. VPC with public and private subnets across 3 AZs
2. NAT Gateway for private subnet internet access
3. Application Load Balancer in public subnets
4. ECS Cluster with Fargate tasks in private subnets
5. RDS PostgreSQL in private subnets with backup
6. ElastiCache Redis in private subnets
7. S3 bucket for static assets with CloudFront
8. IAM roles with least privilege
9. CloudWatch logging and monitoring
10. Use modules for reusability

Provide main.tf, variables.tf, outputs.tf, and module structure.""",
        expected_tokens=1200,
        tags=["terraform", "aws", "infrastructure", "ecs", "vpc"],
    ),

    BenchmarkPrompt(
        id="devops_002",
        name="CI/CD Pipeline",
        category="devops",
        difficulty="medium",
        prompt="""Create a GitHub Actions workflow for a Python project:

1. Run on push to main and PRs
2. Lint with ruff, type-check with mypy
3. Run tests with pytest and coverage
4. Build Docker image
5. Run security scans (bandit, pip-audit)
6. Deploy to staging on main branch
7. Manual approval for production
8. Slack notifications on failure
9. Cache dependencies for speed
10. Matrix testing for Python 3.11, 3.12, 3.13

Provide complete .github/workflows/ci.yml.""",
        expected_tokens=800,
        tags=["github-actions", "ci-cd", "docker", "python"],
    ),

    # Security
    BenchmarkPrompt(
        id="sec_001",
        name="Security Audit Checklist",
        category="security",
        difficulty="medium",
        prompt="""Create a comprehensive security audit checklist for a web application:

1. Authentication & Authorization
2. Input Validation & Sanitization
3. Session Management
4. API Security
5. Data Protection (encryption, PII)
6. Infrastructure Security
7. Logging & Monitoring
7. Incident Response
8. Compliance (GDPR, SOC2, PCI-DSS)

For each category, provide specific testable criteria and tools to use.""",
        expected_tokens=700,
        tags=["security", "audit", "checklist", "compliance"],
    ),

    # Data Analysis
    BenchmarkPrompt(
        id="data_001",
        name="SQL Query Optimization",
        category="data_analysis",
        difficulty="hard",
        prompt="""Optimize this slow PostgreSQL query:

```sql
SELECT u.id, u.email, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE u.created_at > '2023-01-01'
  AND p.category = 'electronics'
  AND o.status IN ('completed', 'shipped')
GROUP BY u.id, u.email
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 100;
```

The tables have millions of rows. Provide:
1. EXPLAIN ANALYZE analysis
2. Index recommendations
3. Query rewrite with CTEs
4. Partitioning strategy
5. Materialized view option""",
        expected_tokens=900,
        tags=["sql", "postgresql", "optimization", "performance"],
    ),

    # AI / Prompt Engineering
    BenchmarkPrompt(
        id="ai_001",
        name="Few-Shot Classification",
        category="ai_prompt_engineering",
        difficulty="medium",
        prompt="""Classify customer support tickets into categories: billing, technical, account, general.

Examples:
Input: "I was charged twice for my subscription"
Output: billing

Input: "The app crashes when I upload a photo"
Output: technical

Input: "How do I change my password?"
Output: account

Input: "Your website looks nice"
Output: general

Now classify: "I can't log in even with the right password" """,
        expected_tokens=300,
        tags=["few-shot", "classification", "nlp"],
    ),

    BenchmarkPrompt(
        id="ai_002",
        name="Chain-of-Thought Reasoning",
        category="ai_prompt_engineering",
        difficulty="medium",
        prompt="""Solve this problem step by step:

A company has 500 employees. 60% are engineers. Of the engineers, 40% are senior. Of the senior engineers, 25% have PhDs. How many senior engineers have PhDs?

Show your reasoning clearly.""",
        expected_tokens=200,
        tags=["chain-of-thought", "reasoning", "math"],
    ),

    # Structured Output
    BenchmarkPrompt(
        id="struct_001",
        name="JSON Schema Generation",
        category="structured_output",
        difficulty="medium",
        prompt="""Generate a JSON schema for a configuration file that defines:

1. Server settings (host, port, workers, timeout)
2. Database config (host, port, name, user, password, pool_size, ssl_mode)
3. Cache config (redis_host, redis_port, ttl, max_memory)
4. Feature flags (array of objects with name, enabled, rollout_percentage)
5. Logging (level, format, output_paths)

The schema should include types, required fields, defaults, and descriptions. Output only the JSON schema.""",
        expected_tokens=600,
        tags=["json-schema", "configuration", "validation"],
    ),

    # Long Context
    BenchmarkPrompt(
        id="long_001",
        name="Large Codebase Analysis",
        category="long_context",
        difficulty="hard",
        prompt="""Analyze this codebase structure and provide a comprehensive architectural review:

[Imagine a large codebase with 50+ files across multiple directories: src/, tests/, docs/, scripts/, configs/

Key areas to analyze:
1. Module organization and dependency graph
2. Separation of concerns (business logic vs infrastructure)
3. Test coverage and quality
4. Configuration management
5. Error handling patterns
6. Logging and observability
7. Security considerations
8. Performance bottlenecks
9. Technical debt hotspots
10. Migration readiness for new framework version

Provide prioritized recommendations with effort estimates.""",
        expected_tokens=1500,
        tags=["architecture", "code-review", "refactoring", "long-context"],
    ),
]


def get_prompts_by_category(category: str) -> list[BenchmarkPrompt]:
    """Get all prompts for a category."""
    return [p for p in BENCHMARK_PROMPTS if p.category == category]


def get_prompts_by_difficulty(difficulty: str) -> list[BenchmarkPrompt]:
    """Get all prompts for a difficulty level."""
    return [p for p in BENCHMARK_PROMPTS if p.difficulty == difficulty]


def get_all_prompts() -> list[BenchmarkPrompt]:
    """Get all benchmark prompts."""
    return BENCHMARK_PROMPTS.copy()


# Category metadata
CATEGORIES = {
    "software_engineering": {"name": "Software Engineering", "count": 3},
    "devops": {"name": "DevOps / Infrastructure", "count": 2},
    "security": {"name": "Security", "count": 1},
    "data_analysis": {"name": "Data Analysis", "count": 1},
    "ai_prompt_engineering": {"name": "AI / Prompt Engineering", "count": 2},
    "structured_output": {"name": "Structured Output", "count": 1},
    "long_context": {"name": "Long Context", "count": 1},
}

DIFFICULTIES = {
    "easy": {"name": "Easy", "count": 0},
    "medium": {"name": "Medium", "count": 8},
    "hard": {"name": "Hard", "count": 5},
}