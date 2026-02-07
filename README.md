# Claude Code Skill Benchmarks

Measures how skill documentation design affects Claude Code's adherence to recommended patterns.

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Verify imports work
python3 -c "from scaffold import verify_environment; print('OK')"

# Run LangChain agent experiment
.venv/bin/python tests/langchain_agent/test_langchain_agent.py -t BASELINE

# Run LangGraph agent experiment
.venv/bin/python tests/langgraph_agent/test_langgraph_agent.py -t BASELINE
```

## Requirements

- Python 3.13+
- Docker (for sandboxed execution of generated code)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY` (for generated agents), `LANGSMITH_API_KEY` (optional)

## How It Works

1. **Setup**: Creates isolated temp directory with skill files, CLAUDE.md, and environment (Dockerfile, requirements.txt, test data)
2. **Run**: Executes Claude Code CLI with a prompt asking it to complete a task
3. **Validate**: Checks generated assets for patterns, runs code in Docker, uses LLM to evaluate output quality
4. **Cleanup**: Removes temp directory

## Experiments

### 1. LangChain Agent (`tests/langchain_agent/`)

Tests whether Claude uses modern patterns (`create_agent`, `@tool`) vs deprecated patterns (`create_sql_agent`).

```bash
.venv/bin/python tests/langchain_agent/test_langchain_agent.py -t control   # CONTROL vs BASELINE
.venv/bin/python tests/langchain_agent/test_langchain_agent.py -t guidance  # Positive vs negative framing
.venv/bin/python tests/langchain_agent/test_langchain_agent.py -t noise     # Progressive noise
```

| Preset | Treatments | Tests |
|--------|------------|-------|
| `control` | CONTROL, BASELINE | Skill vs no skill |
| `guidance` | GUIDANCE_POS, GUIDANCE_NEG | Positive vs negative framing |
| `claudemd` | BASELINE, CLAUDE_MD_POS, CLAUDE_MD_MOVED | CLAUDE.md impact |
| `noise` | BASELINE, NOISE_1, NOISE_2, NOISE_3 | Progressive noise interference |
| `minimal` | BASELINE, MINIMAL, NO_SQL_EXAMPLE | Documentation level |
| `stress` | MINIMAL, MINIMAL_NOISE | Stress tests |

### 2. LangGraph Agent (`tests/langgraph_agent/`)

Tests whether Claude can generate complex multi-agent LangGraph code with proper patterns.

```bash
.venv/bin/python tests/langgraph_agent/test_langgraph_agent.py -t control
.venv/bin/python tests/langgraph_agent/test_langgraph_agent.py -t doc-level
.venv/bin/python tests/langgraph_agent/test_langgraph_agent.py -t noise
```

| Preset | Treatments | Tests |
|--------|------------|-------|
| `control` | CONTROL, BASELINE | Skill vs no skill |
| `doc-level` | MINIMAL, BASIC, FULL | Documentation level |
| `claudemd` | BASELINE, CLAUDE_MD_POS, CLAUDE_MD_NEG | CLAUDE.md impact |
| `noise` | BASELINE, NOISE_1, NOISE_2, NOISE_3 | Progressive noise interference |
| `stress` | MINIMAL, MINIMAL_NOISE, NOISE_CLAUDE_MD | Stress tests |

## Project Structure

```
scaffold/
  __init__.py       # Public API exports
  runner.py         # Test execution, Docker, event parsing
  setup.py          # Environment setup/verification
  framework.py      # Treatment, Validators
  model.py          # LLM evaluation

tests/
  langchain_agent/
    environment/      # Dockerfile, requirements.txt, chinook.db
    config.py         # Treatment definitions
    test_langchain_agent.py
  langgraph_agent/
    environment/      # Dockerfile, requirements.txt
    config.py         # Treatment definitions
    test_langgraph_agent.py

skill_constructs/
  langchain/          # LangChain skill content
  noise/              # Noise/distractor skills
```

## Defining Treatments

```python
from scaffold import Treatment, PythonFileValidator, OutputQualityValidator, MetricsCollector

TREATMENTS = {
    "BASELINE": Treatment(
        description="Skill with positive guidance",
        sections=MY_SKILL_SECTIONS,
        validators=[
            PythonFileValidator(
                "output.py", "Code Check",
                required={"pattern": "description"},
                forbidden={"bad_pattern": "description"},
                require_all=True,
            ),
            OutputQualityValidator(
                "output.py", "Output Check",
                task_description="What the code should do",
                expected_behavior="What good output looks like",
            ),
            MetricsCollector(["output.py"]),
        ],
    ),
    "WITH_NOISE": Treatment(
        description="With distractor tasks",
        sections=MY_SKILL_SECTIONS,
        noise_tasks=["docker-patterns", "react-components"],
        validators=[...],
    ),
}
```

## Validation

Generated code is validated in two ways:

1. **Pattern Matching**: Check for required/forbidden code patterns
2. **Docker Execution**: Run the code in a sandboxed container
3. **LLM Evaluation**: Use GPT-4o-mini to assess if output is meaningful

### LangChain Agent
- **PASS**: Uses `create_agent`/`@tool`, valid syntax, runs, produces expected output
- **FAIL**: Uses deprecated `create_sql_agent`, syntax errors, runtime errors

### LangGraph Agent
- **PASS**: Uses StateGraph, TypedDict, @tool, valid syntax, runs
- **FAIL**: No LangGraph patterns, uses deprecated patterns, errors

## Environment Setup

Each test has an `environment/` directory containing:
- `Dockerfile` - Container image for running generated code
- `requirements.txt` - Python dependencies
- Test data (e.g., `chinook.db` for SQL tests)

The environment is copied to the temp test directory and used to build a Docker image for sandboxed execution.

## Key Findings

| Treatment | Result | Finding |
|-----------|--------|---------|
| LangChain CONTROL (no skill) | FAIL | Uses deprecated `create_sql_agent` |
| LangChain BASELINE (with skill) | PASS | Uses modern `create_agent` + `@tool` |
| LangGraph CONTROL (no skill) | FAIL | Uses raw API, no LangGraph |
| LangGraph BASELINE (with skill) | PASS | Uses StateGraph, TypedDict |

**Conclusion**: Skills have real, measurable impact on Claude's code generation patterns.
