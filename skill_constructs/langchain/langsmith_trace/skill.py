"""LangSmith Trace skill sections."""

FRONTMATTER = """---
name: langsmith-trace
description: "Use this skill for ANY LangSmith/LangChain observability question. Covers two topics: (1) Adding tracing to your application (LangChain/LangGraph or vanilla Python/TS with @traceable), and (2) Querying traces for debugging, analyzing execution flow, and exporting trace data."
---"""

HEADER = """# LangSmith Trace

Two main topics: **adding tracing** to your application, and **querying traces** for debugging and analysis."""

SETUP = """## Setup

### Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_PROJECT=your-project-name                   # Optional: default project
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
```

### Dependencies

```bash
pip install langsmith click rich python-dotenv
```"""

ADDING_TRACING = """## Adding Tracing to Your Application

### LangChain/LangGraph Apps

Just set environment variables — tracing is automatic:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
export OPENAI_API_KEY=<your-openai-api-key>  # or your LLM provider's key
```

Optional variables:
- `LANGSMITH_PROJECT` - specify project name (defaults to "default")
- `LANGCHAIN_CALLBACKS_BACKGROUND=false` - use for serverless to ensure traces complete before function exit

### Non-LangChain/LangGraph Apps

Use the `@traceable` decorator and wrap your LLM client:

```python
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())

@traceable
def my_llm_pipeline(question: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content
```

### Best Practices

- **Apply `@traceable` to all nested functions** you want visible in LangSmith
- **Wrapped clients auto-trace all calls** — `wrap_openai()` records every LLM call
- **Name your traces** for easier filtering: `@traceable(name="retrieve_docs")`
- **Add metadata** for searchability: `@traceable(metadata={"user_id": "123"})`

```python
# Example: nested tracing
@traceable
def rag_pipeline(question: str) -> str:
    docs = retrieve_docs(question)  # traced if @traceable applied
    return generate_answer(question, docs)

@traceable(name="retrieve_docs")
def retrieve_docs(query: str) -> list[str]:
    return docs

@traceable(name="generate_answer")
def generate_answer(question: str, docs: list[str]) -> str:
    return client.chat.completions.create(...)
```"""

QUERYING_TRACES = """## Querying Traces

Navigate to `skills/langsmith-trace/scripts/` to run commands.

### Quick Reference

```bash
# Show recent traces
python query_traces.py recent --limit 10 --project my-project

# Show with metadata (timing, tokens, costs)
python query_traces.py recent --limit 10 --include-metadata

# Filter by time
python query_traces.py recent --last-n-minutes 60
python query_traces.py recent --since 2025-01-20T10:00:00Z

# Get specific trace details
python query_traces.py trace <trace-id> --show-hierarchy

# Export traces to directory (recommended for bulk collection)
python query_traces.py export ./traces --limit 50 --include-metadata
python query_traces.py export ./traces --limit 20 --include-io    # With inputs/outputs
python query_traces.py export ./traces --limit 20 --full          # Everything

# Filter by run type
python query_traces.py export ./traces --run-type tool            # Only tool calls
python query_traces.py export ./traces --run-type llm             # Only LLM calls

# Search by name pattern
python query_traces.py search "agent" --project my-project

# Output as JSON
python query_traces.py recent --format json --limit 5
```"""

COMMANDS = """## Commands

**`recent`** - List recent traces (`--limit`, `--project`, `--last-n-minutes`, `--include-metadata`, `--format`)

**`trace <id>`** - Get specific trace (`--show-hierarchy`, `--include-metadata`, `--output`)

**`export <dir>`** - Bulk export to directory (`--limit`, `--include-metadata`, `--include-io`, `--full`, `--run-type`, `--max-concurrent`)

**`search <pattern>`** - Find runs by name (`--limit`, `--last-n-minutes`)"""

TIPS = """## Tips

- Use `export` for bulk data, always specify `--project`, use `/tmp` for temp files
- Include `--include-metadata` for performance/cost analysis
- Increase `--max-concurrent 10` for large exports
- Use `--format json` with jq for analysis"""

RELATED_SKILLS = """## Related Skills

- Use **langsmith-dataset** skill to generate evaluation datasets from traces
- Use **langsmith-evaluator** skill to create evaluators and measure performance"""

# Default sections used in tests (same as full for this skill)
DEFAULT_SECTIONS = [
    FRONTMATTER,
    HEADER,
    SETUP,
    ADDING_TRACING,
    QUERYING_TRACES,
    COMMANDS,
    TIPS,
    RELATED_SKILLS,
]

# Full sections (same as default for this skill - all sections included)
FULL_SECTIONS = DEFAULT_SECTIONS
