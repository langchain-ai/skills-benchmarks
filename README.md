# Claude Code Skill Benchmarks

Framework for benchmarking skill design best practices with Claude Code CLI.

**Core question**: What makes a skill effective for Claude Code?

## Key Hypotheses

1. **CLAUDE.md matters** - Project-level context improves task completion by providing skill synergy documentation
2. **Documentation format matters** - Well-structured docs with examples outperform minimal or verbose documentation
3. **Skill synergies exist** - Describing how skills work together helps Claude Code chain them effectively

## Quick Start

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env  # Add your API keys

# Run all benchmarks
uv run python tests/run_test_suite.py

# Run specific category
uv run python tests/run_test_suite.py --category context_impact

# List available tests
uv run python tests/run_test_suite.py --list
```

## Test Categories

### 1. Baseline Tests (`tests/baseline/`)
Measure raw Claude Code capability **without** any skill context or CLAUDE.md.

```bash
uv run python tests/run_test_suite.py --category baseline
```

### 2. Context Impact Tests (`tests/context_impact/`)
Compare performance **with vs without** CLAUDE.md to measure its impact.

```bash
uv run python tests/run_test_suite.py --category context_impact
```

Tests run the same prompt with different contexts:
- `ContextMode.NONE` - No CLAUDE.md, no skills
- `ContextMode.CLAUDE_MD_ONLY` - Just CLAUDE.md
- `ContextMode.FULL` - CLAUDE.md + skills directory

### 3. Skill Design Tests (`tests/skill_design/`)
Compare different documentation formats to find what works best.

```bash
uv run python tests/run_test_suite.py --category skill_design
```

Tests three documentation styles:
- **MINIMAL** - Just code snippets
- **STRUCTURED** - Clear sections with examples
- **VERBOSE** - Excessive detail

### 4. Synergy Tests (`tests/synergy/`)
Test multi-skill tasks that require chaining skills together.

```bash
uv run python tests/run_test_suite.py --category synergy
```

Example: Build agent → Generate traces → Query traces → Create dataset

## Project Structure

```
skills/                      # Skills being benchmarked
  langchain-agents/          # LangChain agent building
  langsmith-trace/           # Trace querying
  langsmith-dataset/         # Dataset generation
  langsmith-evaluator/       # Evaluator creation

tests/
  baseline/                  # No-context tests
  context_impact/            # With/without CLAUDE.md
  skill_design/              # Documentation format comparison
  synergy/                   # Multi-skill tasks
  run_test_suite.py          # Main test runner

scaffold/                    # Test framework
  runner.py                  # Claude Code execution
  setup.py                   # Test environment setup
  validators.py              # Result validation
  cleanup.py                 # Cleanup utilities

CLAUDE.md                    # Project context (what we're testing!)
```

## The Role of CLAUDE.md

`CLAUDE.md` is Claude Code's project-level context file. It provides:

1. **Available skills** - What skills exist and their purposes
2. **Modern patterns** - Correct APIs to use (and deprecated ones to avoid)
3. **Skill synergies** - How skills work together
4. **Common workflows** - Step-by-step guides for multi-skill tasks

Our hypothesis: Claude Code performs significantly better when CLAUDE.md describes skill synergies.

## Evaluation Approach

Each test follows: **prompt → trace → checks → score**

### Trace Capture

Tests capture structured JSON traces from Claude Code:
- Tool calls made
- Files created/modified
- Commands run
- Token usage and cost
- Duration

### Validation

Tests use deterministic validators:
```python
validator = TestValidator()
validator.check_file_exists("output.py", test_dir)
validator.check_patterns_present(["modern_api"], summary)
validator.check_patterns_absent(["deprecated_api"], summary)
```

### Comparison Mode

Context impact tests run the same prompt with different contexts:
```python
results = run_comparison_test(
    test_name="My Test",
    prompt=prompt,
    test_dir_factory=create_test_dir,
    validate_func=validate,
    context_modes=[ContextMode.NONE, ContextMode.FULL]
)
```

## Adding New Tests

### Baseline Test (no context)

```python
from scaffold.runner import run_autonomous_test, ContextMode

result = run_autonomous_test(
    test_name="My Test",
    prompt=prompt,
    test_dir=test_dir,
    validate_func=validate,
    context_mode=ContextMode.NONE
)
```

### Comparison Test (with/without context)

```python
from scaffold.runner import run_comparison_test, ContextMode

results = run_comparison_test(
    test_name="My Test",
    prompt=prompt,
    test_dir_factory=lambda: setup_test_environment(),
    validate_func=validate,
    context_modes=[ContextMode.NONE, ContextMode.FULL]
)
```

## Adding New Skills

1. Create `skills/<skill-name>/` directory
2. Add skill documentation (SKILL.md or README.md)
3. Add reference scripts in `scripts/` subdirectory
4. Update CLAUDE.md to describe the skill and its synergies
5. Create tests in `tests/` to benchmark the skill

## Configuration

### Models

```bash
uv run python tests/run_test_suite.py --model sonnet  # default
uv run python tests/run_test_suite.py --model opus
uv run python tests/run_test_suite.py --model haiku
```

### Environment Variables

```bash
LANGSMITH_API_KEY=<your-key>
LANGSMITH_PROJECT=skills
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
```

## Results Analysis

Traces are saved to `logs/traces/` for post-hoc analysis:

```json
{
  "tool_calls": [...],
  "files_created": [...],
  "commands_run": [...],
  "cost_usd": 0.0123,
  "input_tokens": 1500,
  "output_tokens": 800,
  "duration_seconds": 45.2
}
```

Compare across context modes to measure CLAUDE.md impact.
