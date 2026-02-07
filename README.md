# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run all test cases
.venv/bin/python tests/run_test_suite.py

# Run specific cases
.venv/bin/python tests/run_test_suite.py -c SKILL_POS SKILL_NEG

# Run comparison group with repetitions
.venv/bin/python tests/run_test_suite.py --compare framing -r 3
```

## Test Cases

Tests measure whether Claude follows skill guidance to use modern LangChain patterns instead of deprecated `create_sql_agent`.

| Case | Description |
|------|-------------|
| `SKILL_NEG` | Skill with negative guidance ("don't use X") |
| `SKILL_POS` | Skill with positive guidance ("use Y") |
| `SKILL_NONE` | Skill without guidance section |
| `REITERATE_NEG` | Skill + CLAUDE.md, both negative |
| `REITERATE_POS` | Skill + CLAUDE.md, both positive |
| `MOVED_NEG` | Guidance in CLAUDE.md only (negative) |
| `MOVED_POS` | Guidance in CLAUDE.md only (positive) |

## Comparison Groups

```bash
--compare framing      # SKILL_NEG vs SKILL_POS
--compare location     # SKILL_NEG vs MOVED_NEG
--compare reiteration  # SKILL_NEG vs REITERATE_NEG
--compare positive     # All positive framing cases
--compare negative     # All negative framing cases
```

## Project Structure

```
skill_constructs/           # Modular skill sections for testing
  langchain/                # LangChain ecosystem skills
    langchain_agents/       # Agent patterns (sections in skill.py)
    langsmith_*/            # Tracing, datasets, evaluators
  pytest_fixtures/          # Test fixture patterns
  CLAUDE_SAMPLE.md          # Example CLAUDE.md

tests/
  context_impact/           # Context impact tests
    cases.py                # Test case definitions
    helpers.py              # Shared test utilities
    test_langchain_context.py  # Main test script

scaffold/                   # Test infrastructure
  runner.py                 # Test execution
  capture.py                # Event capture/parsing
  setup.py                  # Environment setup
  templates.py              # Skill assembly
```

## Validation Criteria

Tests **pass** if:
1. Skill was read (guidance had chance to influence)
2. create_agent or create_deep_agent was used

Tests **fail** if:
- Skill wasn't discovered/read
- Deprecated pattern was used despite guidance
