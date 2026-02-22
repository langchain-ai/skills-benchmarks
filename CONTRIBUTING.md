# Contributing

## Adding a New Skill

1. **For production use**: Add to `skills/main/<skill-name>/skill.md`
2. **For benchmarking**: Add to `skills/benchmarks/<skill-name>/skill.md`

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

For polyglot skills (Python + TypeScript), create variant files:
- `skill_py.md` - Python-only content
- `skill_ts.md` - TypeScript-only content
- `skill_all.md` - Combined content for both languages

## Adding a New Task

Tasks are self-contained directories under `tasks/`. Tasks are **decoupled from treatments** - any treatment can be used with any task.

```
tasks/my-task/
  instruction.md        # Task prompt with {variable} placeholders
  task.toml             # Task metadata + default_treatments
  environment/          # Docker context
    Dockerfile
    requirements.txt
  validation/
    validators.py       # Function-based validators
  data/                 # Optional: ground truth, test cases
```

### 1. Create task.toml

```toml
[metadata]
name = "my-task"
description = "What this task tests"
difficulty = "medium"  # easy, medium, hard
category = "langchain"  # langsmith, langchain, langgraph, deepagents
tags = ["tag1", "tag2"]
default_treatments = [
    "CONTROL",
    "LCC_CLAUDE_ALL",
    "ALL_MAIN_SKILLS",
]

[template]
required = ["run_id"]

[environment]
dockerfile = "Dockerfile"
timeout_sec = 900

[validation]
validators = ["MyValidator"]
```

### 2. Create instruction.md

```markdown
Create an agent that does X.

Use the run_id `{run_id}` for any resources you create.
```

### 3. Write validators

Validators are functions that return `(passed: list[str], failed: list[str])`:

```python
"""Function-based validators for my-task."""

from pathlib import Path

from scaffold.python.validation import (
    validate_file_exists,
    validate_pattern,
)


def validate_output(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate the generated output."""
    passed, failed = [], []

    output_file = test_dir / "output.json"
    if output_file.exists():
        passed.append("Output: file created")
    else:
        failed.append("Output: file not found")

    return passed, failed


# List of all validators - order matters!
VALIDATORS = [
    validate_output,
]
```

### 4. Run your task

```bash
# Run with specific treatment
uv run pytest tests/tasks/test_tasks.py --task=my-task --treatment=CONTROL -v

# Run with default treatments
uv run pytest tests/tasks/test_tasks.py --task=my-task -v
```

## Adding a New Treatment

Treatments are defined in `treatments/{category}/*.yaml`. Categories:
- `common/` - Shared treatments (CONTROL, ALL_MAIN_SKILLS)
- `langsmith/` - LangSmith skill variations (LS_*)
- `langchain_concise/` - LangChain CLAUDE.md tests (LCC_*)
- `oss_split/` - OSS split skill combinations (OSSS_*)
- `oss_merged/` - OSS merged skill combinations (OSSM_*)

### Treatment YAML Format

```yaml
MY_TREATMENT:
  name: MY_TREATMENT
  description: "What this treatment tests"
  skills:
    - skill: langsmith_trace    # Directory in skills/benchmarks/
      name: langsmith-trace     # Name shown to Claude
      variant: py               # Optional: load skill_py.md
      suffix: true              # Optional: add variant suffix to name

WITH_CLAUDE_MD:
  name: WITH_CLAUDE_MD
  description: "Skill + CLAUDE.md guidance"
  claude_md: |
    # Project Guidelines
    Always check available skills before coding.
  skills:
    - skill: my_skill
      name: my-skill

WITH_NOISE:
  name: WITH_NOISE
  description: "Main skill + noise distractor"
  skills:
    - skill: my_skill
      name: my-skill
    - skill: docker_patterns
      name: docker-patterns
      noise: true              # Mark as noise skill
  noise_tasks:
    - docker_patterns          # Track noise task completion
```

### YAML Anchors for Reuse

Use anchors to share skill lists:

```yaml
# Define anchor
_base_skills: &base_skills
  - skill: langsmith_trace
    name: langsmith-trace

# Reuse with <<: *anchor
MY_TREATMENT:
  skills:
    <<: *base_skills
    - skill: additional_skill
      name: additional-skill
```

## Built-in Validation Utilities

Import from `scaffold.python.validation`:

### Core Utilities

| Function | Purpose |
|----------|---------|
| `validate_file_exists(test_dir, filepath)` | Check file exists |
| `validate_pattern(test_dir, filepath, pattern, desc)` | Check file contains pattern |
| `validate_no_pattern(test_dir, filepath, pattern, desc)` | Check file doesn't contain pattern |
| `validate_skill_invoked(events, skill_name)` | Check if Claude invoked a skill |
| `validate_noise_outputs(test_dir, noise_tasks)` | Check noise task deliverables |
| `validate_skill_scripts(test_dir, outputs, events)` | Track script usage (informational) |

### Dataset Utilities

| Function | Purpose |
|----------|---------|
| `validate_dataset_structure(test_dir, outputs, filename, ...)` | Check dataset JSON structure |
| `validate_trajectory_accuracy(test_dir, outputs, filename, expected_filename, ...)` | Compare against ground truth |
| `validate_dataset_upload(test_dir, outputs, filename, upload_prefix)` | Verify LangSmith upload |

### Docker Execution

| Function | Purpose |
|----------|---------|
| `validate_python_execution(test_dir, script, ...)` | Run Python in Docker |
| `validate_typescript_execution(test_dir, script, ...)` | Run TypeScript in Docker |
| `validate_code_execution(test_dir, outputs, ...)` | Run both Python and TypeScript |

### Tracing Utilities

| Function | Purpose |
|----------|---------|
| `validate_python_tracing(test_dir, filepath, functions)` | Check Python has @traceable |
| `validate_typescript_tracing(test_dir, filepath, functions)` | Check TypeScript has traceable() |
| `validate_langsmith_trace(test_dir, outputs)` | Verify traces in LangSmith |

### Evaluator Utilities

| Function | Purpose |
|----------|---------|
| `validate_evaluator_exists(test_dir, language)` | Find evaluator file |
| `validate_evaluator_syntax(test_dir, language)` | Check evaluator parses |
| `validate_evaluator_patterns(test_dir, language)` | Check evaluator has right patterns |
| `validate_evaluator_logic(test_dir, outputs, test_cases_file)` | Run evaluator against test cases |

## Running Tests

```bash
# Run specific task + treatment
uv run pytest tests/tasks/test_tasks.py --task=ls-lang-tracing --treatment=LS_BASIC_PY -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_CLAUDE_NONE,LCC_CLAUDE_FULL -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* -v

# Run task with default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# With repetitions
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL --count=3 -v

# Parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* --count=2 -n 4 -v

# List all combinations
uv run pytest tests/tasks/test_tasks.py --collect-only
```

### TypeScript (Vitest)

```bash
# Run specific task + treatment
TASK=ls-lang-tracing TREATMENT=LS_BASIC_PY pnpm vitest tests/tasks/test_tasks.test.ts

# With wildcard
TASK=lc-basic TREATMENT=LCC_* pnpm vitest tests/tasks/test_tasks.test.ts

# With parallelism
pnpm vitest tests/tasks/test_tasks.test.ts --pool=threads --poolOptions.threads.maxThreads=4
```

## Experiment Results

Results are saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/experiment_20260217_143052/
  summary.md              # Human-readable results table
  metadata.json           # Experiment config and timing
  events/                 # Parsed events from each run
  raw/                    # Raw Claude CLI output
  reports/                # Per-run validation reports
  artifacts/              # Generated files and execution output
```

The summary shows pass rates, turns, duration, skills invoked, and scripts used for each treatment.

## Design Principles

### Tasks vs Treatments

- **Tasks** define *what* Claude should do (environment, prompt, validators)
- **Treatments** define *how* Claude is configured (skills, CLAUDE.md, noise)
- Any treatment can be used with any task
- `default_treatments` in task.toml defines standard test matrix

### Treatment Naming

Use consistent prefixes:
- `CONTROL` - No skills (baseline)
- `LS_*` - LangSmith treatments
- `LCC_*` - LangChain Concise treatments
- `OSSS_*` - OSS Split Skill treatments
- `OSSM_*` - OSS Merged Skill treatments

### Skill Organization

- `skills/main/` - Production-ready skills
- `skills/benchmarks/` - Skill variations for testing
- `skills/noise/` - Distractor skills for interference tests
