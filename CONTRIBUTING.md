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

Tasks are self-contained directories under `tasks/`:

```
tasks/my-task/
  instruction.md        # Task prompt with {variable} placeholders
  task.toml             # Task metadata
  treatments.yaml       # Treatment configurations
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
difficulty = "basic"  # easy, medium, hard
category = "langsmith"
tags = ["tag1", "tag2"]

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

### 3. Define treatments.yaml

Treatments define skill configurations to test:

```yaml
CONTROL:
  description: "No skills (baseline)"
  skills: []

WITH_SKILL:
  description: "With my-skill"
  skills:
    - skill: my_skill        # Directory name in skills/benchmarks/
      name: my-skill         # Name shown to Claude

WITH_VARIANT:
  description: "Python variant only"
  skills:
    - skill: langsmith_trace
      variant: py            # Load skill_py.md variant
      name: langsmith-trace-py
      suffix: true           # Add -py suffix to skill name

WITH_GUIDANCE:
  description: "Skill + CLAUDE.md guidance"
  claude_md: |
    # Project Guidelines
    Always check available skills before coding.
  skills:
    - skill: my_skill
      name: my-skill

WITH_NOISE:
  description: "Main skill + noise distractor"
  skills:
    - skill: my_skill
      name: my-skill
    - skill: docker_patterns
      name: docker-patterns
      noise: true            # Mark as noise skill
  noise_tasks:
    - docker_patterns        # Track noise task completion
```

### 4. Write validators

Validators are functions that return `(passed: list[str], failed: list[str])`:

```python
"""Function-based validators for my-task."""

from pathlib import Path

from scaffold.python.validation import (
    validate_dataset_structure,
    validate_skill_scripts,
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


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# List of all validators - order matters!
VALIDATORS = [
    validate_output,
    validate_scripts,
]
```

### 5. Add to tasks/index.yaml

```yaml
tasks:
  - name: my-task
    path: my-task
```

### 6. Run your task

```bash
# Run specific treatment
uv run pytest tests/tasks/test_tasks.py -k "my-task and WITH_SKILL" -v

# Run all treatments for the task
uv run pytest tests/tasks/test_tasks.py -k "my-task" -v
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
# Run all tasks
uv run pytest tests/tasks/test_tasks.py -v

# Run specific task
uv run pytest tests/tasks/test_tasks.py -k "ls-multiskill-basic" -v

# Run specific treatment
uv run pytest tests/tasks/test_tasks.py -k "UNIFIED_BOTH" -v

# Run specific combination
uv run pytest tests/tasks/test_tasks.py -k "ls-lang-tracing and UNIFIED_BOTH" -v

# With repetitions
uv run pytest tests/tasks/test_tasks.py -k "ls-lang-tracing and BASELINE" -v --count=3

# List all combinations
uv run pytest tests/tasks/test_tasks.py --collect-only
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
