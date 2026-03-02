# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

> **Note**: Tests default to Claude Sonnet 4.5. Override with `BENCH_CC_MODEL` env var (e.g., `BENCH_CC_MODEL=claude-opus-4-5-20251101`).

## Quick Start

```bash
# Setup
uv sync                      # Python
npm install                   # TypeScript

# Run a specific task with a treatment
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=ALL_MAIN_SKILLS -v

# Run task with its default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# Run with repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL,ALL_MAIN_SKILLS --count=3 -n 4 -v
```

## Requirements

- Python 3.11+ / Node.js 20+
- Docker (for sandboxed execution)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `ANTHROPIC_API_KEY`
- macOS: `brew install coreutils` (provides `gtimeout`)

## Project Structure

```
tasks/                    # Self-contained benchmark tasks
  ls-lang-tracing/        # Each task has its own directory
    instruction.md        # Task prompt with {variable} placeholders
    task.toml             # Metadata + validation config
    environment/          # Docker context (Dockerfile, source code)
    validation/           # Test scripts (run inside Docker)
    data/                 # Ground truth, test cases (optional)

treatments/               # Centralized treatment definitions
  common/                 # Shared treatments (CONTROL, ALL_MAIN_SKILLS)
  langsmith/              # LangSmith-specific treatments (LS_*)
  langchain_concise/      # LangChain concise treatments (LCC_*)
  oss_split/              # OSS split skill treatments (OSSS_*)
  oss_merged/             # OSS merged skill treatments (OSSM_*)

skills/
  main/                   # Production skills
  benchmarks/             # Benchmark skill variations
  noise/                  # Distractor skills for interference tests

scaffold/
  python/                 # Python scaffold
    validation/runner.py  # TestRunner for writing check functions
    validation/core.py    # Validation helpers (patterns, skills, noise)
    utils.py              # Docker orchestration
    tasks.py              # Task loader (reads task.toml)
  typescript/             # TypeScript scaffold (mirrors Python)
    validation/runner.ts  # TestRunner (same API as Python)
    validation/core.ts    # Validation helpers
    utils.ts              # Docker orchestration
    tasks.ts              # Task loader

tests/
  tasks/
    test_tasks.py         # Main test runner (pytest)
    test_tasks.test.ts    # Main test runner (vitest)
  scripts/                # Script unit tests (Python/TypeScript parity)
```

## Tasks

Tasks are decoupled from treatments — any treatment can be used with any task. Each task defines `default_treatments` in its `task.toml`.

| Task | Category | Description |
|------|----------|-------------|
| `lc-basic` | langchain | SQL analytics agent |
| `lc-basic-noise` | langchain | Skill retention with noise distractors |
| `lc-deps-tavily` | langchain | Fix broken LangChain dependencies |
| `lc-framework-choice` | langchain | Framework selection for different use cases |
| `ls-lang-tracing` | langsmith | Add LangSmith tracing to Python/TypeScript agents |
| `ls-lang-evaluator` | langsmith | Create LangSmith evaluators from datasets |
| `ls-multiskill-basic` | langsmith | Create trajectory dataset from traces |
| `ls-multiskill-advanced` | langsmith | Create dataset + evaluator pipeline |
| `oss-fix-lg-persistence` | langgraph | Fix LangGraph persistence bugs |
| `oss-fix-lg-execution` | langgraph | Fix LangGraph parallel execution bugs |
| `oss-fix-lc-streaming` | langchain | Fix LangChain streaming bugs |
| `oss-fix-lc-hitl` | langchain | Fix LangChain human-in-the-loop bugs |
| `oss-fix-da-memory` | deepagents | Fix Deep Agents memory bugs |

## Treatments

Treatments define skill configurations. They're organized by category:

| Prefix | Category | Description |
|--------|----------|-------------|
| `CONTROL` | common | No skills (baseline) |
| `ALL_MAIN_SKILLS` | common | All production skills |
| `LS_*` | langsmith | LangSmith skill variations |
| `LCC_*` | langchain_concise | LangChain CLAUDE.md and guidance tests |
| `OSSS_*` | oss_split | OSS split skill combinations |
| `OSSM_*` | oss_merged | OSS merged skill combinations |

## Running Tests

### Python (pytest) — recommended for benchmark runs

```bash
# Run specific task + treatment(s)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=ALL_MAIN_SKILLS -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL,ALL_MAIN_SKILLS -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* -v

# Run task with default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# With repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL --count=3 -n 4 -v

# List all available combinations
uv run pytest tests/tasks/test_tasks.py --collect-only
```

### TypeScript (vitest)

The vitest runner executes the same validation pipeline and is useful for setup verification and TypeScript development. **Use pytest for benchmark runs** — vitest threads cannot parallelize Docker execution, so multiple treatments run sequentially.

```bash
# Run specific task + treatment
TASK=lc-basic TREATMENT=ALL_MAIN_SKILLS npx vitest run tests/tasks/test_tasks.test.ts

# List test cases without running (like pytest --collect-only)
npx vitest list tests/tasks/test_tasks.test.ts
```

## How It Works

1. **Setup**: Creates isolated temp directory with skills, CLAUDE.md, and environment files
2. **Run**: Executes Claude Code CLI in Docker (`--dangerously-skip-permissions` for headless operation)
3. **Validate**: Runs test scripts in Docker against Claude's artifacts (config-driven via `task.toml`)
4. **Report**: Logs results to local experiment directory and LangSmith
5. **Cleanup**: Removes temp directory and test resources (LangSmith datasets/projects)

## Results

### LangSmith

Results are tracked as [LangSmith experiments](https://docs.smith.langchain.com/evaluation). Each pytest invocation creates an experiment under the `skills-benchmark` dataset, where every task/treatment combination becomes a row with logged inputs, outputs, and feedback scores (pass rate, duration, turns). When `TRACE_TO_LANGSMITH=true`, Claude Code traces are nested under experiment rows — click a row to see the full session trace (all turns, LLM calls, and tool calls). See `.env.example` for configuration.

### Local

Results are also saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/experiment_20260217_143052/
  summary.md              # Results table with pass rates
  metadata.json           # Experiment config
  events/                 # Parsed events per run
  raw/                    # Raw Claude CLI output
  reports/                # Validation reports
  artifacts/              # Files Claude created (not infrastructure)
```

Example summary output:

```
Treatment                    Checks          Turns    Dur      Skills
----------------------------------------------------------------------------
ALL_MAIN_SKILLS              9/9 (100%)      11       45s      langchain-fundamentals
CONTROL                      8/11 (73%)      14       78s      none
```

## LangSmith Tasks

Tasks prefixed with `ls-` query and create LangSmith resources. Important considerations:

> **Note: Parallel execution**
>
> Parallel execution via pytest-xdist (`-n 4`) is tested and safe — each worker gets isolated LangSmith projects. Running multiple separate pytest processes simultaneously is untested and may have issues.

> **Warning: Orphaned resources on interrupt**
>
> If tests are interrupted (Ctrl+C), LangSmith resources may not be cleaned up:
> - **Projects**: Delete `benchmark-*` projects older than a few hours
> - **Datasets**: Delete `bench-*` datasets with UUID suffixes
>
> Normal test completion auto-cleans these resources.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for adding new tasks, skills, treatments, and test scripts.
