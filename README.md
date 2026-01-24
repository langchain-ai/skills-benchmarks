# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run all test cases
.venv/bin/python tests/basic_skill/test_langchain_context.py

# Run specific cases
.venv/bin/python tests/basic_skill/test_langchain_context.py -c SKILL_POS SKILL_NEG

# Run preset group
.venv/bin/python tests/basic_skill/test_langchain_context.py -c framing

# Run with repetitions
.venv/bin/python tests/basic_skill/test_langchain_context.py -c SKILL_POS -r 3
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
| `MINIMAL` | Minimal skill - overview + quick ref only |
| `NO_SQL_EXAMPLE` | No SQL example - general patterns only |

## Presets

```bash
-c framing        # SKILL_NEG, SKILL_POS
-c location       # SKILL_NEG, MOVED_NEG
-c reiteration    # SKILL_NEG, REITERATE_NEG
-c difficulty     # SKILL_POS, NO_SQL_EXAMPLE, MINIMAL
-c minimal-boost  # MINIMAL, MINIMAL_REITERATE, MINIMAL_MOVED
```

## Project Structure

```
skill_constructs/           # Modular skill sections for testing
  langchain/langchain_agents/  # Agent patterns (sections in skill.py)

tests/basic_skill/          # Basic skill tests
  cases.py                  # Test case definitions + validators
  test_langchain_context.py # Main test script

scaffold/                   # Test infrastructure
  runner.py                 # Test execution
  logs.py                   # Event capture/parsing + reports
  setup.py                  # Environment setup + skill assembly
```

## Validation Criteria

Tests **pass** if:
1. langchain-agents skill was invoked
2. File was created with valid syntax
3. Uses modern patterns (create_agent, @tool)
4. Agent runs without errors

Tests **fail** if:
- Skill wasn't invoked
- Deprecated import (create_sql_agent)
- Syntax/runtime errors
