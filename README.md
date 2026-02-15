# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

> **Note**: Tests were conducted with Opus 4.5, early February 2026.

## Quick Start (Python)

```bash
# Setup
uv sync

# Run single test
uv run pytest tests/bench_ls_multiskill/test_advanced.py -k "ADV_ALL_SECTIONS" -v

# Run with repetitions
uv run pytest tests/bench_ls_multiskill/test_advanced.py -k "ADV_ALL_SECTIONS" -v --count=3

# Run in parallel (6 workers)
uv run pytest tests/bench_ls_multiskill/test_advanced.py -v -n 6
```

## Quick Start (TypeScript)

```bash
# Setup
npm install

# Build TypeScript
npm run build

# Run example test
npx vitest run tests/example/guidance.test.ts

# Run in parallel (3 workers)
npx vitest run tests/example/guidance.test.ts --pool=threads
```

## Requirements

- Python 3.13+ (for Python tests) or Node.js 20+ (for TypeScript tests)
- Docker (for sandboxed execution of generated code)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY` (for generated agents), `LANGSMITH_API_KEY` (for LangSmith experiments), `ANTHROPIC_API_KEY` (for LLM evaluation)
- macOS only: `brew install coreutils` (provides `gtimeout` for test timeouts)

---

## Understanding the Repository

### Benchmark vs Main Skills

This repository has two types of skills with different purposes:

| Directory | Purpose | Tests Expected to Pass? |
|-----------|---------|------------------------|
| `skills/main/` | **Production skills** - Complete, well-documented skills ready for use | Yes, all tests should pass |
| `skills/benchmarks/` | **Benchmark skills** - May use weakened/partial versions to test specific behaviors | No, some treatments are *designed* to fail |

**Why benchmark tests fail**: Benchmark experiments test how Claude responds to different skill configurations. For example, a `CONTROL` treatment with no skills tests Claude's baseline capability - it's *expected* to fail because Claude doesn't have the guidance it needs.

**Benchmark skill organization**: Skills in `skills/benchmarks/` are organized by the benchmark they support. It's fine to have "duplicate" skills with distinct names if they're testing different configurations:

```
skills/benchmarks/
  langchain_basic/        # For bench_lc_basic tests
    skill.md
  langsmith_trace/        # For bench_ls_multiskill tests
    skill.md
    scripts/
  langsmith_dataset/
    skill.md
    scripts/
```

---

## Contributing

### Adding a New Skill

1. **For production use**: Add to `skills/main/<skill-name>/skill.md`
2. **For benchmarking**: Add to `skills/benchmarks/<benchmark-name>/<skill-name>/skill.md`

Skills follow a standard format with YAML frontmatter and XML sections:

```markdown
---
name: my-skill
description: Brief description for skill matching
---

<oneliner>
One sentence explaining what this skill does.
</oneliner>

<setup>
Environment variables and dependencies needed.
</setup>

<usage>
How to use the skill with examples.
</usage>

<!-- Add more sections as needed -->
```

### Adding a New Benchmark Test

Tests use **treatments** (different skill configurations) and **validators** (checks for success).

#### 1. Create a test file

For Python (pytest):
```
tests/my_benchmark/
  __init__.py
  conftest.py           # Optional: shared fixtures
  environment/          # Docker context
    Dockerfile
    requirements.txt
  test_mytest.py        # Your test file
```

For TypeScript (vitest):
```
tests/my_benchmark/
  config.ts             # Treatment definitions
  mytest.test.ts        # Your test file
```

#### 2. Define treatments

Treatments define what skill content and CLAUDE.md to inject:

```python
# Python example
from scaffold import Treatment, PythonFileValidator, MetricsCollector

TREATMENTS = {
    # Control: no skills - tests baseline capability (expected to fail)
    "CONTROL": Treatment(
        description="No skill, no CLAUDE.md",
        validators=[
            PythonFileValidator("agent.py", required={"pattern": "def run"}),
            MetricsCollector(["agent.py"]),
        ],
    ),

    # With skill: tests if skill guidance helps (expected to pass)
    "WITH_SKILL": Treatment(
        description="Full skill content",
        skills={"my-skill": my_skill_sections},
        claude_md="Check skills before coding.",
        validators=[
            PythonFileValidator("agent.py", required={"pattern": "recommended_pattern"}),
            MetricsCollector(["agent.py"]),
        ],
    ),
}
```

#### 3. Write the test

```python
import pytest
from scaffold.python import extract_events, parse_output

@pytest.mark.parametrize("treatment_name", list(TREATMENTS.keys()))
def test_treatment(treatment_name, test_dir, setup_test_context, run_claude, record_result):
    treatment = TREATMENTS[treatment_name]

    # Setup: inject skills and CLAUDE.md into temp directory
    setup_test_context(skills=treatment.skills, claude_md=treatment.claude_md)

    # Run: execute Claude with prompt
    result = run_claude("Build an agent that does X", timeout=300)

    # Parse output events
    events = extract_events(parse_output(result.stdout))

    # Validate: run all validators
    passed, failed = treatment.validate(events, test_dir)

    # Record results for summary
    record_result(events, passed, failed)

    # Assert (CONTROL may fail, that's OK)
    assert not failed, f"Validation failed: {failed}"
```

### Available Validators

| Validator | Purpose | Example |
|-----------|---------|---------|
| `PythonFileValidator` | Check file exists with required/forbidden patterns | `PythonFileValidator("agent.py", required={"@tool": "Uses @tool decorator"})` |
| `SkillInvokedValidator` | Check if Claude invoked a specific skill | `SkillInvokedValidator("my-skill", required=True)` |
| `OutputQualityValidator` | LLM-based evaluation of output quality | `OutputQualityValidator(criteria="Code follows best practices")` |
| `NoiseTaskValidator` | Check that noise/distractor tasks were ignored | `NoiseTaskValidator(noise_tasks)` |
| `MetricsCollector` | Collect metrics (turns, duration, files) | `MetricsCollector(["agent.py"])` |

### Validator Examples

**Pattern matching:**
```python
PythonFileValidator(
    "agent.py",
    required={
        "create_react_agent": "Uses modern LangGraph pattern",
        "@tool": "Defines tools with decorator",
    },
    forbidden={
        "create_sql_agent": "Avoids deprecated pattern",
    },
)
```

**LLM evaluation:**
```python
OutputQualityValidator(
    criteria="The agent correctly queries the database and returns accurate results",
    input_files=["agent.py"],
    output_file="output.txt",
)
```

---

## How It Works

1. **Setup**: Creates isolated temp directory with skill files, CLAUDE.md, and environment (Dockerfile, requirements.txt, test data)
2. **Run**: Executes Claude Code CLI with a prompt asking it to complete a task
3. **Validate**: Checks generated assets for patterns, runs code in Docker, uses LLM to evaluate output quality
4. **Cleanup**: Removes temp directory and any test resources (e.g., LangSmith datasets)

---

## Project Structure

```
skills/
  main/             # Production skills (complete, all tests pass)
  benchmarks/       # Benchmark skills (may be weakened for testing)
  noise/            # Noise/distractor skills for interference tests

scaffold/
  python/           # Python scaffold (pytest) - Treatment, validators, utils
  typescript/       # TypeScript scaffold (vitest) - mirrors Python
  shell/            # Shared shell scripts (docker.sh, setup.sh)

tests/
  bench_lc_basic/        # Basic single-skill benchmark
  bench_ls_multiskill/   # Multi-skill LangSmith benchmark

logs/experiments/        # Test results output
```

---

## Validation Details

Generated code is validated via:

1. **Pattern Matching** (`PythonFileValidator`): Check for required/forbidden code patterns
2. **Docker Execution**: Run the code in a sandboxed container
3. **LLM Evaluation** (`OutputQualityValidator`): Use GPT-4o-mini to assess output quality
4. **API Verification**: Check LangSmith uploads (for multi-skill tests)
5. **Skill Invocation** (`SkillInvokedValidator`): Verify Claude loaded the right skills

---

## Existing Experiments

### 1. Basic Benchmark (`tests/bench_lc_basic/`)

Tests whether Claude uses modern patterns (`create_react_agent`, `@tool`) vs deprecated patterns (`create_sql_agent`).

```bash
# Run specific treatments
uv run pytest tests/bench_lc_basic/ -k "CONTROL or ALL_SECTIONS" -v

# Run with repetitions
uv run pytest tests/bench_lc_basic/ -k "CONTROL" -v --count=3

# Run all treatments in parallel
uv run pytest tests/bench_lc_basic/ -v -n 4
```

| Treatment | Description | Expected |
|-----------|-------------|----------|
| `CONTROL` | No skill, no CLAUDE.md (pure baseline) | May fail |
| `ALL_SECTIONS` | Full skill sections + full CLAUDE.md | Pass |
| `BASELINE` | Skill with positive guidance | Pass |
| `GUIDANCE_POS/NEG` | Positive vs negative framing | Pass |
| `CLAUDE_MD_*` | CLAUDE.md content variations | Varies |
| `NOISE_1/2/3` | Progressive noise interference | Varies |

### 2. LangSmith Benchmark (`tests/bench_ls_multiskill/`)

Tests whether Claude can use multiple skills together (trace → dataset → evaluator pipeline).

Each pytest-xdist worker gets its own LangSmith project for isolation, so parallel execution is safe.

```bash
# Basic (2 skills: trace + dataset)
uv run pytest tests/bench_ls_multiskill/test_basic.py -v

# Advanced (3 skills: trace + dataset + evaluator)
uv run pytest tests/bench_ls_multiskill/test_advanced.py -v

# Run specific treatment with repetitions
uv run pytest tests/bench_ls_multiskill/test_advanced.py -k "ADV_ALL_SECTIONS" -v --count=3

# Run all treatments in parallel (6 workers)
uv run pytest tests/bench_ls_multiskill/test_advanced.py -v -n 6
```

| Treatment | Description | Expected |
|-----------|-------------|----------|
| `*_CONTROL` | No skills, no CLAUDE.md (pure baseline) | Fail |
| `*_BASELINE` | Skills without workflow hints | May fail |
| `*_CLAUDEMD` | Workflow rules in CLAUDE.md only | Pass |
| `*_SKILLS` | Workflow hints in skills only | May fail |
| `*_BOTH` | Workflow rules in both | Pass |
| `*_ALL_SECTIONS` | Full skill sections + full CLAUDE.md | Pass |

---

## Experiment Results

Results are saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/experiment_20260205_111553/
  summary.md              # Human-readable results summary
  metadata.json           # Experiment config and timing
  reports/                # Per-run detailed reports
    basic_control_rep1_report.json
    ...
```

- **`summary.md`** - Start here. Shows checks passed per treatment with breakdowns.
- **`reports/*.json`** - Raw data with all checks passed/failed and metrics.
