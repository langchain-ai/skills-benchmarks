# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

> **Note**: Tests default to Claude Sonnet 4.5. Override with `CC_MODEL` env var (e.g., `CC_MODEL=claude-opus-4-5-20251101`).

## Quick Start

```bash
# Setup
uv sync                      # Python
pnpm install && pnpm build   # TypeScript

# Run a specific task with specific treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-advanced --treatment=LS_CLAUDE_ADVANCED_NONE,LS_CLAUDE_ADVANCED_FULL -v

# Run with wildcard pattern (all treatments starting with prefix)
uv run pytest tests/tasks/test_tasks.py --task=ls-lang-tracing --treatment=LS_BASIC_* -v

# Run task with its default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# Run with repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_CLAUDE_* --count=2 -n 4 -v
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
    task.toml             # Metadata + default_treatments
    environment/          # Docker context
    validation/           # Validators
    data/                 # Ground truth (optional)

treatments/               # Centralized treatment definitions
  common/                 # Shared treatments (CONTROL, ALL_MAIN_SKILLS)
  langsmith/              # LangSmith-specific treatments (LS_*)
  langchain_concise/      # LangChain concise treatments (LCC_*)
  oss_split/              # OSS split skill treatments (OSSS_*)
  oss_merged/             # OSS merged skill treatments (OSSM_*)

skills/
  main/                   # Production skills (all tests should pass)
  benchmarks/             # Benchmark skills (variations for testing)
  noise/                  # Distractor skills for interference tests

scaffold/
  python/                 # Python scaffold (pytest)
    tasks.py              # Task loader
    treatments.py         # Treatment builder
  typescript/             # TypeScript scaffold (vitest)
    tasks.ts              # Task loader
    treatments.ts         # Treatment builder

tests/
  tasks/                  # Main test runner
    test_tasks.py         # Python tests (pytest)
    test_tasks.test.ts    # TypeScript tests (vitest)
  scripts/                # Script unit tests (Python/TypeScript parity)
```

## Tasks

Tasks are decoupled from treatments - any treatment can be used with any task. Each task defines `default_treatments` in its `task.toml` for standard testing.

| Task | Category | Description |
|------|----------|-------------|
| `ls-lang-tracing` | langsmith | Add LangSmith tracing to Python/TypeScript agents |
| `ls-lang-evaluator` | langsmith | Create LangSmith evaluators from datasets |
| `ls-multiskill-basic` | langsmith | Create trajectory dataset from traces |
| `ls-multiskill-advanced` | langsmith | Create dataset + evaluator pipeline |
| `lc-basic` | langchain | SQL analytics agent (tests skill/guidance variations) |
| `lc-basic-noise` | langchain | Skill retention with noise distractors |
| `lc-deps-tavily` | langchain | Fix broken LangChain dependencies |
| `lc-framework-choice` | langchain | Framework selection task |
| `lc-version-confusion` | langchain | Modernize legacy LangChain code |
| `oss-fix-lg-persistence` | langgraph | Fix LangGraph persistence bugs |
| `oss-fix-lc-streaming` | langchain | Fix LangChain streaming bugs |
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

```bash
# Run specific task + treatment(s)
uv run pytest tests/tasks/test_tasks.py --task=ls-lang-tracing --treatment=LS_BASIC_PY -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_CLAUDE_NONE,LCC_CLAUDE_FULL -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_GUIDANCE_* -v

# Run task with default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# With repetitions
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL --count=3 -v

# Parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* --count=2 -n 4 -v

# List all available combinations
uv run pytest tests/tasks/test_tasks.py --collect-only
```

### TypeScript (Vitest)

```bash
# Run specific task + treatment
TASK=ls-lang-tracing TREATMENT=LS_BASIC_PY pnpm vitest tests/tasks/test_tasks.test.ts

# With wildcard
TASK=lc-basic TREATMENT=LCC_CLAUDE_* pnpm vitest tests/tasks/test_tasks.test.ts

# With parallelism
pnpm vitest tests/tasks/test_tasks.test.ts --pool=threads --poolOptions.threads.maxThreads=4
```

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
  artifacts/              # Generated files
```

Example summary output:

```
Treatment                    Checks          Turns    Dur      Skills
----------------------------------------------------------------------------
LS_BASIC_PY                  17/17 (100%)    51       228s     langsmith-trace
LS_CLAUDE_ADVANCED_FULL      5/8 (62%)       12       95s      langsmith-dataset
```

## How It Works

1. **Setup**: Creates isolated temp directory with skills, CLAUDE.md, and environment
2. **Run**: Executes Claude Code CLI with task prompt
3. **Validate**: Runs function-based validators on generated artifacts
4. **Cleanup**: Removes temp directory and test resources (LangSmith datasets/projects)

## LangSmith Tasks

Tasks prefixed with `ls-` query and create LangSmith resources. Important considerations:

> **Note: Parallel execution**
>
> Parallel execution via pytest-xdist (`-n 4`) is tested and safe - each worker gets isolated LangSmith projects. Running multiple separate pytest processes simultaneously is untested and may have issues.

> **Warning: Orphaned resources on interrupt**
>
> If tests are interrupted (Ctrl+C), LangSmith resources may not be cleaned up:
> - **Projects**: Delete `benchmark-*` projects older than a few hours
> - **Datasets**: Delete `bench-*` datasets with UUID suffixes
>
> Normal test completion auto-cleans these resources.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new skills
- Adding new tasks
- Adding new treatments
- Writing validators
