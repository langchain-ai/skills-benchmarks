# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run all experiments
.venv/bin/python tests/basic_skill/test_langchain_context.py

# Run specific experiments
.venv/bin/python tests/basic_skill/test_langchain_context.py -e SKILL_POS SKILL_NEG

# Run preset group
.venv/bin/python tests/basic_skill/test_langchain_context.py -e framing

# Run with repetitions
.venv/bin/python tests/basic_skill/test_langchain_context.py -e SKILL_POS -r 3
```

## Experiments

Experiments measure whether Claude follows skill guidance to use modern LangChain patterns instead of deprecated `create_sql_agent`.

| Experiment | Description |
|------------|-------------|
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
-e framing        # SKILL_NEG, SKILL_POS
-e location       # SKILL_NEG, MOVED_NEG
-e reiteration    # SKILL_NEG, REITERATE_NEG
-e difficulty     # SKILL_POS, NO_SQL_EXAMPLE, MINIMAL
-e minimal-boost  # MINIMAL, MINIMAL_REITERATE, MINIMAL_MOVED
```

## Project Structure

```
skill_constructs/           # Modular skill sections for testing
  langchain/langchain_agents/  # Agent patterns (sections in skill.py)

tests/basic_skill/          # Basic skill experiments
  experiments.py            # Experiment definitions + validators
  test_langchain_context.py # Main test script

scaffold/                   # Test infrastructure
  runner.py                 # Test execution
  logs.py                   # Event capture/parsing + reports
  setup.py                  # Environment setup + skill assembly
```

## Validation Criteria

Experiments **pass** if:
1. langchain-agents skill was invoked
2. File was created with valid syntax
3. Uses modern patterns (create_agent, @tool)
4. Agent runs without errors

Experiments **fail** if:
- Skill wasn't invoked
- Deprecated import (create_sql_agent)
- Syntax/runtime errors
