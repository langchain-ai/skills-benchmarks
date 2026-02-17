---
name: langsmith-trace-py
description: "Use this skill for ANY LangSmith/LangChain observability question. Covers two topics: (1) Adding tracing to your application, and (2) Querying traces. Assists with debugging, analyzing execution flow, and exporting trace data."
---

<oneliner>
Two main topics: **adding tracing** to your application, and **querying traces** for debugging and analysis.
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_PROJECT=your-project-name                   # Optional: default project
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
```

Dependencies

```bash
pip install langsmith click rich python-dotenv
```
</setup>

<trace_langchain_oss>
For LangChain/LangGraph apps, tracing is automatic. Just set environment variables:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
export OPENAI_API_KEY=<your-openai-api-key>  # or your LLM provider's key
```

Optional variables:
- `LANGSMITH_PROJECT` - specify project name (defaults to "default")
- `LANGCHAIN_CALLBACKS_BACKGROUND=false` - use for serverless to ensure traces complete before function exit
</trace_langchain_oss>

<trace_other_frameworks>
For non-LangChain apps, use the `@traceable` decorator and wrap your LLM client:

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

# Nested tracing example
@traceable
def rag_pipeline(question: str) -> str:
    docs = retrieve_docs(question)
    return generate_answer(question, docs)

@traceable(name="retrieve_docs")
def retrieve_docs(query: str) -> list[str]:
    return docs

@traceable(name="generate_answer")
def generate_answer(question: str, docs: list[str]) -> str:
    return client.chat.completions.create(...)
```

Best Practices:
- **Apply `@traceable` to all nested functions** you want visible in LangSmith
- **Wrapped clients auto-trace all calls** — `wrap_openai()` records every LLM call
- **Name your traces** for easier filtering: `@traceable(name="retrieve_docs")`
- **Add metadata** for searchability: `@traceable(metadata={"user_id": "123"})`
</trace_other_frameworks>

<traces_vs_runs>
Use the included scripts to query trace data.

**Understanding the difference is critical:**

- **Trace** = A complete execution tree (root run + all child runs). A trace represents one full agent invocation with all its LLM calls, tool calls, and nested operations.
- **Run** = A single node in the tree (one LLM call, one tool call, etc.)

**Generally, query traces first** — they provide complete context and preserve hierarchy needed for trajectory analysis and dataset generation.
</traces_vs_runs>

<command_structure>
Two command groups with consistent behavior:

```
query_traces.py
├── traces (operations on trace trees - USE THIS FIRST)
│   ├── list    - List traces (filters apply to root run)
│   ├── get     - Get single trace with full hierarchy
│   └── export  - Export traces to JSONL files (one file per trace)
│
└── runs (operations on individual runs - for specific analysis)
    ├── list    - List runs (flat, filters apply to any run)
    ├── get     - Get single run
    └── export  - Export runs to single JSONL file (flat)
```

**Key differences:**

| | `traces *` | `runs *` |
|---|---|---|
| Filters apply to | Root run only | Any matching run |
| `--run-type` | Not available | Available |
| Returns | Full hierarchy | Flat list |
| Export output | Directory (one file/trace) | Single file |
</command_structure>

<querying_traces>
```bash
# List recent traces (most common operation)
python query_traces.py traces list --limit 10 --project my-project

# List traces with metadata (timing, tokens, costs)
python query_traces.py traces list --limit 10 --include-metadata

# Filter traces by time
python query_traces.py traces list --last-n-minutes 60
python query_traces.py traces list --since 2025-01-20T10:00:00Z

# Get specific trace with full hierarchy
python query_traces.py traces get <trace-id>

# List traces and show hierarchy inline
python query_traces.py traces list --limit 5 --show-hierarchy

# Export traces to JSONL (one file per trace, includes all runs)
python query_traces.py traces export ./traces --limit 20 --full
python query_traces.py traces export ./traces --limit 10 --include-io

# Filter traces by performance
python query_traces.py traces list --min-latency 5.0 --limit 10    # Slow traces (>= 5s)
python query_traces.py traces list --error --last-n-minutes 60     # Failed traces

# Export specific traces by ID
python query_traces.py traces export ./traces --trace-ids abc123,def456 --full

# Stitch multiple JSONL files together
cat ./traces/*.jsonl > all_traces.jsonl

# --- RUNS (for specific analysis) ---

# List specific run types (flat list)
python query_traces.py runs list --run-type llm --limit 20         # LLM calls only
python query_traces.py runs list --name "ChatOpenAI" --limit 10    # By name pattern

# Get a specific run by ID
python query_traces.py runs get <run-id> --full

# Export LLM runs for analysis
python query_traces.py runs export ./llm_runs.jsonl --run-type llm --limit 100 --full
```
</querying_traces>

<filters>
All commands support these filters (all AND together):

**Basic filters:**
- `--trace-ids abc,def` - Filter to specific traces
- `--limit N` - Max results
- `--project NAME` - Project name
- `--last-n-minutes N` - Time filter
- `--since TIMESTAMP` - Time filter (ISO format)
- `--error / --no-error` - Error status
- `--name PATTERN` - Name contains (case-insensitive)

**Performance filters:**
- `--min-latency SECONDS` - Minimum latency (e.g., `5` for >= 5s)
- `--max-latency SECONDS` - Maximum latency
- `--min-tokens N` - Minimum total tokens
- `--tags tag1,tag2` - Has any of these tags

**Advanced filter:**
- `--filter QUERY` - Raw LangSmith filter query for complex cases (feedback, metadata, etc.)

```bash
# Example: Filter by feedback score
python query_traces.py traces list --filter 'and(eq(feedback_key, "correctness"), gte(feedback_score, 0.8))'
```
</filters>

<export_format>
Export creates `.jsonl` files (one run per line) with these fields:
```json
{"run_id": "...", "trace_id": "...", "name": "...", "run_type": "...", "parent_run_id": "...", "inputs": {...}, "outputs": {...}}
```

Use `--include-io` or `--full` to include inputs/outputs (required for dataset generation).
</export_format>

<tips>
- **Start with traces** — they provide complete context needed for trajectory and dataset generation
- Use `traces export --full` for bulk data destined for datasets
- Always specify `--project` to avoid mixing data from different projects
- Use `/tmp` for temporary exports
- Include `--include-metadata` for performance/cost analysis
- Stitch files: `cat ./traces/*.jsonl > all.jsonl`
</tips>

