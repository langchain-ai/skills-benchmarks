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
python tests/langchain_agent/test_langchain_agent.py -t CONTROL ALL_SECTIONS -r 3

# Run LangSmith synergy experiment
python tests/langsmith_synergy/test_langsmith_synergy.py -t ADV_CONTROL ADV_ALL_SECTIONS -r 3 --skip-traces
```

## Requirements

- Python 3.13+
- Docker (for sandboxed execution of generated code)
- Claude Code CLI (`claude`)
- API keys: `OPENAI_API_KEY` (for generated agents), `LANGSMITH_API_KEY` (for LangSmith experiments)

## How It Works

1. **Setup**: Creates isolated temp directory with skill files, CLAUDE.md, and environment (Dockerfile, requirements.txt, test data)
2. **Run**: Executes Claude Code CLI with a prompt asking it to complete a task
3. **Validate**: Checks generated assets for patterns, runs code in Docker, uses LLM to evaluate output quality
4. **Cleanup**: Removes temp directory and LangSmith test datasets

## Experiments

### 1. LangChain Agent (`tests/langchain_agent/`)

Tests whether Claude uses modern patterns (`create_agent`, `@tool`) vs deprecated patterns (`create_sql_agent`).

```bash
python tests/langchain_agent/test_langchain_agent.py -t CONTROL ALL_SECTIONS -r 3
python tests/langchain_agent/test_langchain_agent.py -t GUIDANCE_POS GUIDANCE_NEG -r 3
```

| Treatment | Description |
|-----------|-------------|
| `CONTROL` | No skill, no CLAUDE.md (pure baseline) |
| `ALL_SECTIONS` | Full skill sections + full CLAUDE.md |
| `BASELINE` | Skill with positive guidance |
| `GUIDANCE_POS/NEG` | Positive vs negative framing |
| `CLAUDE_MD_*` | CLAUDE.md content variations |
| `NOISE_1/2/3` | Progressive noise interference |

### 2. LangSmith Synergy (`tests/langsmith_synergy/`)

Tests whether Claude can use multiple skills together (trace → dataset → evaluator pipeline).

**Important**: Only run one LangSmith experiment at a time. The experiment generates traces in LangSmith and uses "most recent 5 traces" for ground truth. Running multiple experiments simultaneously can cause race conditions where traces from different runs interfere with each other.

```bash
# Basic (2 skills: trace + dataset)
python tests/langsmith_synergy/test_langsmith_synergy.py -t basic -r 3 -w 3

# Advanced (3 skills: trace + dataset + evaluator)
python tests/langsmith_synergy/test_langsmith_synergy.py -t advanced -r 3 -w 3
```

| Treatment | Description |
|-----------|-------------|
| `*_CONTROL` | No skills, no CLAUDE.md (pure baseline) |
| `*_BASELINE` | Skills without workflow hints |
| `*_CLAUDEMD` | Workflow rules in CLAUDE.md only |
| `*_SKILLS` | Workflow hints in skills only |
| `*_BOTH` | Workflow rules in both |
| `*_ALL_SECTIONS` | Full skill sections + full CLAUDE.md |

## Project Structure

```
scaffold/
  __init__.py       # Public API exports
  runner.py         # Test execution, Docker, event parsing
  setup.py          # Environment setup/verification
  framework.py      # Treatment, Validators
  model.py          # LLM evaluation

tests/
  langchain_agent/  # Modern LangChain patterns
  langsmith_synergy/# Multi-skill workflows

skill_constructs/
  langchain/        # LangChain/LangSmith skill content
  noise/            # Noise/distractor skills
  CLAUDE_SAMPLE.md  # Sample CLAUDE.md with skill synergies
```

## Defining Treatments

```python
from scaffold import Treatment, PythonFileValidator, OutputQualityValidator, MetricsCollector
from skill_constructs import CLAUDE_SAMPLE

TREATMENTS = {
    "CONTROL": Treatment(
        description="No skill, no CLAUDE.md",
        validators=[...],
    ),
    "ALL_SECTIONS": Treatment(
        description="Full skill + CLAUDE.md",
        skills={"my-skill": FULL_SECTIONS},
        claude_md=CLAUDE_SAMPLE,
        validators=[...],
    ),
}
```

## Validation

Generated code is validated via:

1. **Pattern Matching**: Check for required/forbidden code patterns
2. **Docker Execution**: Run the code in a sandboxed container
3. **LLM Evaluation**: Use GPT-4o-mini to assess output quality
4. **API Verification**: Check LangSmith uploads (for synergy tests)
