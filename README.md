# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.
Note: Tests were conducted with Opus 4.5, early February 2026.

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

# Run all basic treatments
uv run pytest tests/bench_ls_multiskill/test_basic.py -v
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

# Run with watch mode
npx vitest tests/example/guidance.test.ts
```

## Requirements

- Python 3.13+ (for Python tests) or Node.js 20+ (for TypeScript tests)
- Docker (for sandboxed execution of generated code)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY` (for generated agents), `LANGSMITH_API_KEY` (for LangSmith experiments), `ANTHROPIC_API_KEY` (for LLM evaluation)
- macOS only: `brew install coreutils` (provides `gtimeout` for test timeouts)

## How It Works

1. **Setup**: Creates isolated temp directory with skill files, CLAUDE.md, and environment (Dockerfile, requirements.txt, test data)
2. **Run**: Executes Claude Code CLI with a prompt asking it to complete a task
3. **Validate**: Checks generated assets for patterns, runs code in Docker, uses LLM to evaluate output quality
4. **Cleanup**: Removes temp directory and LangSmith test datasets

## Experiments

### 1. Basic Benchmark (`tests/bench_lc_basic/`)

Tests whether Claude uses modern patterns (`create_agent`, `@tool`) vs deprecated patterns (`create_sql_agent`).

```bash
# Run specific treatments
uv run pytest tests/bench_lc_basic/ -k "CONTROL or ALL_SECTIONS" -v

# Run with repetitions
uv run pytest tests/bench_lc_basic/ -k "CONTROL" -v --count=3

# Run all treatments in parallel
uv run pytest tests/bench_lc_basic/ -v -n 4
```

| Treatment | Description |
|-----------|-------------|
| `CONTROL` | No skill, no CLAUDE.md (pure baseline) |
| `ALL_SECTIONS` | Full skill sections + full CLAUDE.md |
| `BASELINE` | Skill with positive guidance |
| `GUIDANCE_POS/NEG` | Positive vs negative framing |
| `CLAUDE_MD_*` | CLAUDE.md content variations |
| `NOISE_1/2/3` | Progressive noise interference |

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

# Run with repetitions in parallel
uv run pytest tests/bench_ls_multiskill/test_advanced.py -v -n 6 --count=2
```

| Treatment | Description |
|-----------|-------------|
| `*_CONTROL` | No skills, no CLAUDE.md (pure baseline) |
| `*_BASELINE` | Skills without workflow hints |
| `*_CLAUDEMD` | Workflow rules in CLAUDE.md only |
| `*_SKILLS` | Workflow hints in skills only |
| `*_BOTH` | Workflow rules in both |
| `*_ALL_SECTIONS` | Full skill sections + full CLAUDE.md |

## Project Structure

```
scaffold/
  python/           # Python scaffold (pytest)
    __init__.py     # Public API exports
    schema.py       # Treatment, NoiseTask, Validator
    validation.py   # 5 validators
    utils.py        # Shell wrappers, LLM evaluation
    logging.py      # Event parsing, ExperimentLogger
  typescript/       # TypeScript scaffold (vitest)
    index.ts        # Public API exports
    schema.ts       # Treatment, NoiseTask types
    validation.ts   # 5 validators (mirrors Python)
    utils.ts        # Shell wrappers, LLM evaluation
    logging.ts      # Event parsing, ExperimentLogger
  shell/            # Shared shell scripts
    docker.sh       # Docker operations
    setup.sh        # Environment setup

tests/
  conftest.py          # Python fixtures
  fixtures.ts          # TypeScript fixtures
  bench_lc_basic/     # Basic single-skill benchmark
  bench_ls_multiskill/ # Multi-skill LangSmith benchmark
  example/             # TypeScript example test

skills/
  benchmarks/       # Frozen benchmark skills (XML sections for experiments)
  main/             # Active skills for development and publication
  noise/            # Noise/distractor skills
  CLAUDE.md         # Sample CLAUDE.md with skill synergies
```

## Defining Treatments

### Python

```python
from scaffold import Treatment, PythonFileValidator, OutputQualityValidator, MetricsCollector
from skills import CLAUDE_FULL

TREATMENTS = {
    "CONTROL": Treatment(
        description="No skill, no CLAUDE.md",
        validators=[...],
    ),
    "ALL_SECTIONS": Treatment(
        description="Full skill + CLAUDE.md",
        skills={"my-skill": FULL_SECTIONS},
        claude_md=CLAUDE_FULL,
        validators=[...],
    ),
}
```

### TypeScript

```typescript
import type { Treatment } from '@skills-benchmark/scaffold';
import { PythonFileValidator, MetricsCollector } from '@skills-benchmark/scaffold';

const TREATMENTS: Record<string, Treatment> = {
  CONTROL: {
    description: "No skill, no CLAUDE.md",
    validators: [
      new PythonFileValidator("output.py", { required: { pattern: "desc" } }),
      new MetricsCollector(["output.py"]),
    ],
  },
  BASELINE: {
    description: "With skill",
    skills: { "my-skill": [SKILL_CONTENT] },
    validators: [...],
  },
};
```

## Experiment Results

Results are saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/ls_basic_20260205_111553/
  summary.md              # Human-readable results summary
  metadata.json           # Experiment config and timing
  reports/                # Per-run detailed reports
    basic_control_rep1_report.json
    basic_control_rep2_report.json
    ...
```

- **`summary.md`** - Start here. Shows checks passed per treatment, column breakdowns, and detailed results per run.
- **`reports/*.json`** - Raw data with all checks passed/failed, event logs, and metrics.

## Validation

Generated code is validated via:

1. **Pattern Matching**: Check for required/forbidden code patterns
2. **Docker Execution**: Run the code in a sandboxed container
3. **LLM Evaluation**: Use GPT-4o-mini to assess output quality
4. **API Verification**: Check LangSmith uploads (for synergy tests)
