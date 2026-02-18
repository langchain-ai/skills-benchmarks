# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

> **Note**: Tests conducted with Opus 4.5, February 2026.

## Quick Start

```bash
# Setup
uv sync                      # Python
npm install && npm run build # TypeScript

# Run a single task/treatment
uv run pytest tests/tasks/test_tasks.py -k "ls-lang-tracing and UNIFIED_BOTH" -v

# Run all treatments for a task
uv run pytest tests/tasks/test_tasks.py -k "ls-multiskill-basic" -v

# With repetitions
uv run pytest tests/tasks/test_tasks.py -k "lc-basic-guidance and GUIDANCE_POS" -v --count=3
```

## Requirements

- Python 3.13+ / Node.js 20+
- Docker (for sandboxed execution)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `ANTHROPIC_API_KEY`
- macOS: `brew install coreutils` (provides `gtimeout`)

## Project Structure

```
tasks/                    # Self-contained benchmark tasks
  ls-lang-tracing/        # Each task has its own directory
    instruction.md        # Task prompt
    task.toml             # Metadata
    treatments.yaml       # Treatment configurations
    environment/          # Docker context
    validation/           # Validators
    data/                 # Ground truth (optional)

skills/
  main/                   # Production skills (all tests should pass)
  benchmarks/             # Benchmark skills (may be weakened for testing)
  noise/                  # Distractor skills for interference tests

scaffold/
  python/                 # Python scaffold (pytest)
    tasks.py              # Task loader
    treatments.py         # Treatment builder
    validation/           # Validation utilities
  typescript/             # TypeScript scaffold (vitest)

tests/
  tasks/                  # Main test runner
    test_tasks.py         # Parameterized task/treatment tests
  scripts/                # Script unit tests (Python/TypeScript parity)
```

## Tasks

Each task is a self-contained benchmark with its own treatments:

| Task | Description | Treatments |
|------|-------------|------------|
| `ls-lang-tracing` | Add LangSmith tracing to Python/TypeScript agents | SEPARATE_NAMES, UNIFIED_BOTH, UNIFIED_PY_ONLY, UNIFIED_TS_ONLY, CONTROL |
| `ls-lang-evaluator` | Create LangSmith evaluators from datasets | SEPARATE_NAMES, UNIFIED_BOTH, UNIFIED_PY_ONLY, UNIFIED_TS_ONLY, CONTROL |
| `ls-multiskill-basic` | Create trajectory dataset from traces | BASELINE, CLAUDEMD, SKILLS, BOTH, ALL_SECTIONS, CONTROL |
| `ls-multiskill-advanced` | Create dataset + evaluator pipeline | BASELINE, CLAUDEMD, SKILLS, BOTH, ALL_SECTIONS, CONTROL |
| `lc-basic-claudemd` | Test CLAUDE.md content variations | CONTROL, ALL_SECTIONS, BASELINE, CLAUDE_MD_* |
| `lc-basic-guidance` | Test positive vs negative guidance framing | GUIDANCE_POS, GUIDANCE_NEG |
| `lc-basic-noise` | Test skill retention with noise tasks | NOISE_BASELINE, NOISE_1, NOISE_2, NOISE_3 |

## Running Tests

```bash
# List all available task/treatment combinations
uv run pytest tests/tasks/test_tasks.py --collect-only

# Run specific combination
uv run pytest tests/tasks/test_tasks.py -k "ls-lang-tracing and UNIFIED_BOTH" -v

# Run all treatments for a task
uv run pytest tests/tasks/test_tasks.py -k "ls-multiskill-basic" -v

# Run multiple tasks
uv run pytest tests/tasks/test_tasks.py -k "lc-basic" -v
```

## Results

Results are saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/experiment_20260217_143052/
  summary.md              # Results table with pass rates
  metadata.json           # Experiment config
  events/                 # Parsed events per run
  raw/                    # Raw Claude CLI output
  reports/                # Validation reports
  artifacts/              # Generated files
```

Example summary output:

```
Treatment                    Checks          Turns    Dur      Skills
----------------------------------------------------------------------------
ls-lang-tracing-UNIFIED_BOTH 17/17 (100%)    51       228s     langsmith-trace
ls-multiskill-basic-BASELINE 5/8 (62%)       12       95s      langsmith-dataset
```

## How It Works

1. **Setup**: Creates isolated temp directory with skills, CLAUDE.md, and environment
2. **Run**: Executes Claude Code CLI with task prompt
3. **Validate**: Runs function-based validators on generated artifacts
4. **Cleanup**: Removes temp directory and test resources (LangSmith datasets/projects)

## LangSmith Tasks

Tasks prefixed with `ls-` query and create LangSmith resources. Important considerations:

> **Warning: Single pytest process only**
>
> LangSmith project isolation (via pytest-xdist workers) only works within a single pytest run. Do **not** run multiple separate pytest processes for `ls-*` tasks simultaneously - they may conflict on LangSmith resources.

> **Warning: Orphaned resources on interrupt**
>
> If tests are interrupted (Ctrl+C), LangSmith resources may not be cleaned up:
> - **Projects**: Delete `benchmark-main-*` projects older than a few hours
> - **Datasets**: Delete `test-*` datasets with UUID suffixes

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new skills
- Adding new tasks
- Writing validators
- Treatment configuration options
