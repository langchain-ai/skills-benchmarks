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

Tasks are self-contained directories under `tasks/`. Tasks are **decoupled from treatments** — any treatment can be used with any task.

```
tasks/my-task/
  instruction.md        # Task prompt with {variable} placeholders
  task.toml             # Task metadata + validation config
  environment/          # Docker context
    Dockerfile
    requirements.txt
  validation/           # Test scripts (run inside Docker)
    test_my_task.py
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
default_treatments = ["CONTROL", "ALL_MAIN_SKILLS"]

[template]
required = ["run_id"]

[environment]
dockerfile = "Dockerfile"
timeout_sec = 900

[validation]
test_scripts = "test_my_task.py"       # Script(s) to run in Docker
target_artifacts = ["output.py"]       # File(s) Claude should create (checked before running tests)
timeout = 120                          # Docker execution timeout
```

### 2. Create instruction.md

```markdown
Create an agent that does X.

Use the run_id `{run_id}` for any resources you create.
```

### 3. Write a test script

Test scripts run inside Docker. Use `TestRunner` to handle all boilerplate — you just write check functions that call `runner.passed()` or `runner.failed()`.

```python
"""Test script for my-task. Runs in Docker via task.toml config."""
from scaffold.python.validation.runner import TestRunner


def check_file_exists(runner: TestRunner):
    """Artifact file exists and is readable."""
    source = runner.read(runner.artifacts[0])
    if source:
        runner.passed("file exists")
    else:
        runner.failed("file not found or empty")


def check_has_pattern(runner: TestRunner):
    """Contains expected pattern."""
    source = runner.read(runner.artifacts[0])
    if "expected_pattern" in source:
        runner.passed("has expected pattern")
    else:
        runner.failed("missing expected pattern")


def check_runs(runner: TestRunner):
    """Code executes without errors."""
    output = runner.execute(runner.artifacts[0])
    if output is not None:
        runner.passed(f"produced output ({len(output)} chars)")


if __name__ == "__main__":
    TestRunner.run([check_file_exists, check_has_pattern, check_runs])
```

**TestRunner provides:**
- `runner.artifacts` — target artifact paths from `task.toml` `[validation].target_artifacts`
- `runner.context` — run context dict (run_id, events, treatment_name, etc.)
- `runner.read(path)` — read any file's contents (returns "" if not found)
- `runner.execute(path)` — run a file as subprocess, return stdout
- `runner.load_module(path)` — import a Python file and return the module (cached)
- `runner.passed(msg)` / `runner.failed(msg)` — record check results

Each check function **must** call `runner.passed()` or `runner.failed()` at least once — not calling either is treated as an error.

**Paths inside Docker match local structure:**
- `runner.artifacts[0]` — files Claude created (at workspace root)
- `data/expected.json` — ground truth from `tasks/my-task/data/`
- `validation/helper.py` — other scripts from `tasks/my-task/validation/`

### 4. Run your task

```bash
# Run with specific treatment
uv run pytest tests/tasks/test_tasks.py --task=my-task --treatment=CONTROL -v

# Run with default treatments
uv run pytest tests/tasks/test_tasks.py --task=my-task -v

# Via TypeScript (vitest)
RUN_CLAUDE=true TASK=my-task TREATMENT=CONTROL npx vitest run tests/tasks/test_tasks.test.ts
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

Test scripts running in Docker can import helpers from `scaffold.python.validation`. These are utilities your test scripts call inside check functions.

### Core (`scaffold.python.validation.core`)

| Function | Purpose |
|----------|---------|
| `load_test_context()` | Load run context dict (auto-called by TestRunner) |
| `write_test_results(results)` | Write JSON results (auto-called by TestRunner) |
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
| `check_evaluator_upload(test_dir, outputs)` | Verify upload to LangSmith |

### LLM Evaluation (`scaffold.python.utils`)

| Function | Purpose |
|----------|---------|
| `evaluate_with_schema(prompt)` | LLM judge returning `{"pass": bool, "reason": str}` |

## Running Tests

### Python (pytest)

```bash
# Run specific task + treatment
uv run pytest tests/tasks/test_tasks.py --task=ls-lang-tracing --treatment=LS_BASIC_PY -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL,ALL_MAIN_SKILLS -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* -v

# Run task with default treatments
uv run pytest tests/tasks/test_tasks.py --task=ls-multiskill-basic -v

# With repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL --count=3 -n 4 -v

# List all combinations
uv run pytest tests/tasks/test_tasks.py --collect-only
```

### TypeScript (vitest)

The vitest runner executes the same validation pipeline as pytest and is useful for TypeScript contributors who prefer the vitest workflow. However, **use pytest for benchmark runs** — vitest threads cannot parallelize Docker execution (they block on `spawnSync`), so multiple treatments run sequentially regardless of thread count.

```bash
# Run specific task + treatment (RUN_CLAUDE=true required for full execution)
RUN_CLAUDE=true TASK=ls-lang-tracing TREATMENT=ALL_MAIN_SKILLS npx vitest run tests/tasks/test_tasks.test.ts

# Setup verification only (no Claude execution) — useful for checking task/treatment config
npx vitest run tests/tasks/test_tasks.test.ts
```

Both runners execute the same validation pipeline: `task.toml` → `loadValidators()` → `makeExecutionValidator()` → Docker test scripts. Test scripts can be in Python or TypeScript — both scaffolds are copied into Docker.

## Experiment Results

Results are saved to `logs/experiments/<experiment_id>/`:

```
logs/experiments/experiment_20260217_143052/
  summary.md              # Human-readable results table
  metadata.json           # Experiment config and timing
  events/                 # Parsed events from each run
  raw/                    # Raw Claude CLI output
  reports/                # Per-run validation reports
  artifacts/              # Only files Claude created (not infrastructure)
```

The summary shows pass rates, turns, duration, skills invoked, and scripts used for each treatment.

## Design Principles

### Tasks vs Treatments

- **Tasks** define *what* Claude should do (environment, prompt, validation)
- **Treatments** define *how* Claude is configured (skills, CLAUDE.md, noise)
- Any treatment can be used with any task
- `default_treatments` in task.toml defines the standard test matrix

### Validation

- Test scripts define checks, `task.toml` wires them up — no `validators.py` boilerplate needed
- `target_artifacts` is a gate: if specified, existence is checked before running tests
- Inside test scripts, `runner.read()` and `runner.execute()` can access any file in the workspace
- Docker paths match local paths: `data/`, `validation/`, artifacts at root

### Treatment Naming

Use consistent prefixes:
- `CONTROL` - No skills (baseline)
- `ALL_MAIN_SKILLS` - All production skills
- `LS_*` - LangSmith treatments
- `LCC_*` - LangChain Concise treatments
- `OSSS_*` - OSS Split Skill treatments
- `OSSM_*` - OSS Merged Skill treatments

### Skill Organization

- `skills/main/` - Production-ready skills
- `skills/benchmarks/` - Skill variations for testing
- `skills/noise/` - Distractor skills for interference tests
