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

```

### 2. Create instruction.md

```markdown
Create an agent that does X.

Use the run_id `{run_id}` for any resources you create.
```

### 3. Write a test script

Test scripts run inside Docker. Use `TestRunner` to handle all boilerplate — you just write check functions that call `runner.passed()` or `runner.failed()`.

```python
"""Test script for my-task. Runs in Docker via make_execution_validator."""
from scaffold.python.validation.runner import TestRunner


def check_file_exists(runner):
    """Artifact file exists and is readable."""
    source = runner.read(runner.artifacts[0])
    if source:
        runner.passed("file exists")
    else:
        runner.failed("file not found or empty")


def check_has_pattern(runner):
    """Contains expected pattern."""
    source = runner.read(runner.artifacts[0])
    if "expected_pattern" in source:
        runner.passed("has expected pattern")
    else:
        runner.failed("missing expected pattern")


def check_runs(runner):
    """Code executes without errors."""
    output = runner.execute()
    if output is not None:
        runner.passed(f"produced output ({len(output)} chars)")
    else:
        runner.failed("execution failed")


if __name__ == "__main__":
    TestRunner.run([check_file_exists, check_has_pattern, check_runs])
```

**TestRunner provides:**
- `runner.artifacts` — list of artifact paths as passed from validators.py
- `runner.context` — run context (run_id, events, etc.)
- `runner.read(path)` — read any file's contents
- `runner.execute(path)` — run a file as subprocess, return stdout
- `runner.passed(msg)` / `runner.failed(msg)` — record results

Each check function **must** call `runner.passed()` or `runner.failed()` — not calling either is an error.

### 4. Wire up with the factory

`validators.py` just calls `make_execution_validator`:

```python
from pathlib import Path
from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_my_task.py",
    target_artifacts="output.py",
)

VALIDATORS = [validate_execution]
```

The factory handles:
- Copying test scripts + scaffold validation helpers into Docker
- Serializing `outputs` dict to `_test_context.json` for test script access
- Running the test script and parsing JSON results
- Supports `str | list[str]` for both `test_script` and `target_artifacts`

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

## Validation Helpers

Test scripts running in Docker can import helpers from `scaffold.python.validation`. These are **not standalone validators** — they're utilities your test scripts call.

### Core (`scaffold.python.validation.core`)

| Function | Purpose |
|----------|---------|
| `load_test_context(path="_test_context.json")` | Load outputs dict serialized by the factory |
| `check_file_exists(test_dir, filepath)` | Check file exists |
| `check_pattern(filepath, pattern, desc)` | Check file contains regex pattern |
| `check_no_pattern(filepath, pattern, desc)` | Check file doesn't contain pattern |
| `check_skill_invoked(outputs, skill_name)` | Check if Claude invoked a skill |
| `check_starter_skill_first(outputs)` | Check starter skill was invoked first |
| `check_noise_outputs(noise_tasks, test_dir=".")` | Check noise task deliverables |

### Dataset (`scaffold.python.validation.dataset`)

| Function | Purpose |
|----------|---------|
| `check_dataset_structure(filename, ...)` | Check dataset JSON structure |
| `check_trajectory_accuracy(filename, expected_filename, ...)` | Compare against ground truth |
| `check_dataset_upload(filename, upload_prefix, ...)` | Verify LangSmith upload |

### Evaluator (`scaffold.python.validation.evaluator`)

| Function | Purpose |
|----------|---------|
| `find_evaluator_function(content, language)` | Find evaluator function name |
| `check_evaluator_exists(test_dir, outputs)` | Find evaluator files |
| `check_evaluator_upload(test_dir, outputs)` | Verify upload to LangSmith |

### LLM Evaluation (`scaffold.python.utils`)

| Function | Purpose |
|----------|---------|
| `evaluate_with_schema(prompt)` | LLM judge returning `{"pass": bool, "reason": str}` |

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

> **Note:** The TypeScript test runner does not currently support function-based validators or LLM-as-judge evaluation. Validation logic (including `evaluate_with_schema` and `trace_feedback` evaluator tracing) is only available in the Python runner.

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
