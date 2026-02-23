# Skills Project Guidelines

## Python/TypeScript Parity

**CRITICAL:** LangSmith skills have both Python and TypeScript implementations. These MUST stay in sync:
- Same CLI commands, flags, and options
- Same output format for identical inputs
- Same error handling behavior

When modifying any script, always update both Python and TypeScript versions together. Parity tests in `tests/scripts/langsmith/parity/` verify this.

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

## Benchmark Validation Principles

When creating or updating validators:

1. **Separate infrastructure failures from Claude failures** - Infrastructure issues (Docker, missing files) should be clearly distinguishable from Claude's task performance

2. **Validators should be precise** - A validator that's too lax won't catch real issues; one that's too strict will fail on valid solutions

3. **Always verify validators manually** - After running tests:
   - Check the raw logs to see exactly what Claude did
   - Review artifacts to verify the validator's assessment was correct
   - Look for both false positives (passed when it shouldn't) and false negatives (failed when it shouldn't)

4. **Informational stats vs hard failures**:
   - Use `passed` list for informational stats (e.g., "Skills invoked: langsmith-trace")
   - Use `failed` list only for actual task failures
   - Skill invocations and script usage are tracked as stats, not failures

5. **Task specification clarity** - If Claude fails in unexpected ways, consider whether:
   - The task prompt is ambiguous
   - The validator is checking the wrong thing
   - Claude genuinely didn't understand or execute correctly

## Test Running Best Practices

1. Run tests multiple times before drawing conclusions
2. Always inspect raw logs and artifacts for every run (including passes)
3. Document findings about validator accuracy and task difficulty
4. Track patterns across treatments to understand skill effectiveness

## Running Tests

Use the `--task` and `--treatment` CLI options for targeted test runs:

```bash
# Run specific task + treatment
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_CLAUDE_ALL -v

# Multiple treatments (comma-separated)
uv run pytest tests/tasks/test_tasks.py --task=ls-evaluator --treatment=LS_BASIC_PY,LS_WORKFLOW_PY -v

# Wildcard patterns
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_* -v

# With repetitions and parallel workers
uv run pytest tests/tasks/test_tasks.py --task=lc-basic --treatment=LCC_CLAUDE_ALL --count=2 -n 4 -v
```

## Project Structure

### Treatments
Treatments are centralized in `treatments/` folder by category:
- `common/` - CONTROL, ALL_MAIN_SKILLS
- `langsmith/` - LS_* treatments
- `langchain_concise/` - LCC_* treatments
- `oss_split/` - OSSS_* treatments (granular skills)
- `oss_merged/` - OSSM_* treatments (consolidated skills)

Tasks and treatments are **decoupled** - any treatment can be used with any task.

### Tasks
Each task has `default_treatments` in its `task.toml`. When running without `--treatment`, the defaults are used.

## Linting

Use ruff for both linting and formatting:
```bash
uv run ruff check .           # Check for issues
uv run ruff check --fix .     # Auto-fix issues
uv run ruff format .          # Format code
```

## Stacked PRs

For large refactors, use stacked PRs:

1. Create base branch from main with first set of commits
2. Create subsequent branches from previous branch
3. Push all branches: `git push origin branch1 branch2 branch3`
4. Create PRs with appropriate base branches
5. After merging each PR, rebase subsequent branches onto main:
   ```bash
   git fetch origin main
   git checkout -B next-branch origin/main
   git cherry-pick <commit-hash>
   git push origin next-branch --force
   ```

## TypeScript Parity

The TypeScript scaffold (`scaffold/typescript/`) mirrors Python:
- Uses `smol-toml` for TOML parsing (same behavior as Python's tomllib)
- Uses Node.js native `globSync` for file matching
- `buildTreatmentSkills()` doesn't support `included_sections`, `section_overrides`, `extra_sections`
- For full section manipulation, use Python implementation
