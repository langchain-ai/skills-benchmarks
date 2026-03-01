# Skills Project Guidelines

## Python/TypeScript Parity

**CRITICAL:** LangSmith skills have both Python and TypeScript implementations. These MUST stay in sync:
- Same CLI commands, flags, and options
- Same output format for identical inputs
- Same error handling behavior

When modifying any script, always update both Python and TypeScript versions together. Parity tests in `tests/scripts/langsmith/parity/` verify this.

The TypeScript scaffold (`scaffold/typescript/`) mirrors Python:
- Both scaffolds are copied into Docker so test scripts in either language work from either runner
- `TestRunner` class available in both languages with identical API
- `buildTreatmentSkills()` in TS doesn't support `included_sections`, `section_overrides`, `extra_sections` — use Python for full section manipulation

## Skill Markdown File Parity

Each skill directory contains variant files that MUST stay aligned:
- `skill_py.md` - Python-only content
- `skill_ts.md` - TypeScript/JavaScript-only content
- `skill_all.md` - Combined content for both languages

When updating skill documentation:
1. All three files should have the same **section structure** (headers, order)
2. Code examples should be equivalent implementations in each language
3. CLI commands should show the appropriate language-specific invocation
4. Keep descriptions consistent across variants

## Task Structure

Each task is a self-contained directory:

```
tasks/my-task/
  task.toml             # Metadata + validation config
  instruction.md        # Task prompt with {variable} placeholders
  environment/          # Docker context (Dockerfile, requirements.txt, source code)
  validation/           # Test scripts (run inside Docker)
  data/                 # Ground truth, test cases (optional)
```

Validation is config-driven via `task.toml`:

```toml
[validation]
test_scripts = "test_my_task.py"       # Script(s) to run in Docker
target_artifacts = ["output.py"]       # File(s) Claude should create
timeout = 120                          # Docker execution timeout
```

The framework auto-builds a validator from this config — no `validators.py` needed.

Docker paths mirror the local structure: `data/`, `validation/`, artifacts at root. Contributors can reference paths the same way locally and in Docker.

## Benchmark Validation Principles

When creating or updating test scripts:

1. **Separate infrastructure failures from Claude failures** — infrastructure issues (Docker, missing files) should be clearly distinguishable from Claude's task performance

2. **Validators should be precise** — a validator that's too lax won't catch real issues; one that's too strict will fail on valid solutions

3. **Always verify validators manually** — after running tests:
   - Check the raw logs to see exactly what Claude did
   - Review artifacts to verify the validator's assessment was correct
   - Look for both false positives (passed when it shouldn't) and false negatives (failed when it shouldn't)

4. **Informational stats vs hard failures**:
   - Use `passed` list for informational stats (e.g., "Skills invoked: langsmith-trace")
   - Use `failed` list only for actual task failures
   - Skill invocations and script usage are tracked as stats, not failures

5. **Every check must call passed() or failed()** — returning without calling either is treated as an error by TestRunner

## Running Tests

### Python (pytest)

```bash
# Run specific task + treatment
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=ALL_MAIN_SKILLS -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL,ALL_MAIN_SKILLS -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* -v

# With repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=CONTROL --count=3 -n 4 -v
```

### TypeScript (vitest)

```bash
# Run specific task + treatment (RUN_CLAUDE=true required for full execution)
RUN_CLAUDE=true TASK=lc-basic TREATMENT=ALL_MAIN_SKILLS npx vitest run tests/tasks/test_tasks.test.ts

# With parallelism
RUN_CLAUDE=true TASK=lc-basic TREATMENT=CONTROL,ALL_MAIN_SKILLS npx vitest run tests/tasks/test_tasks.test.ts --pool=threads --poolOptions.threads.maxThreads=2

# Setup verification only (no Claude execution)
npx vitest run tests/tasks/test_tasks.test.ts
```

Both runners execute the same validation pipeline and produce equivalent results.

### Best Practices

1. Run tests multiple times before drawing conclusions
2. Always inspect raw logs and artifacts for every run (including passes)
3. Document findings about validator accuracy and task difficulty
4. Track patterns across treatments to understand skill effectiveness

## Project Structure

### Treatments
Treatments are centralized in `treatments/` folder by category:
- `common/` - CONTROL, ALL_MAIN_SKILLS
- `langsmith/` - LS_* treatments
- `langchain_concise/` - LCC_* treatments
- `oss_split/` - OSSS_* treatments (granular skills)
- `oss_merged/` - OSSM_* treatments (consolidated skills)

Tasks and treatments are **decoupled** — any treatment can be used with any task.

### Tasks
Each task has `default_treatments` in its `task.toml`. When running without `--treatment`, the defaults are used.

### Skills
- `skills/main/` - Production-ready skills
- `skills/benchmarks/` - Skill variations for testing
- `skills/noise/` - Distractor skills for interference tests

## Linting

```bash
# Python
uv run ruff check .           # Check for issues
uv run ruff check --fix .     # Auto-fix issues
uv run ruff format .          # Format code

# TypeScript
npm run typecheck              # Type checking
npm test                       # Run vitest (unit + parity tests)
```
