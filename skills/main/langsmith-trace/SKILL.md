---
name: langsmith-trace
description: "INVOKE THIS SKILL when working with LangSmith tracing OR querying traces. Covers adding tracing to applications and querying/exporting trace data. Uses the langsmith CLI tool."
---

<oneliner>
Two main topics: **adding tracing** to your application, and **querying traces** for debugging and analysis. Python and Javascript implementations are both supported.
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_PROJECT=your-project-name                   # Optional: default project
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
```

**IMPORTANT:** Always check the environment variables or `.env` file for `LANGSMITH_PROJECT` before querying or interacting with LangSmith. This tells you which project contains the relevant traces and data. If the LangSmith project is not available, use your best judgement to identify the right one.

CLI Tool
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
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
- `LANGCHAIN_CALLBACKS_BACKGROUND=false` - use for serverless to ensure traces complete before function exit (Python)
</trace_langchain_oss>

<trace_other_frameworks>
For anything other than LangChain/LangGraph, **read the matching reference file in `references/` before writing tracing code**. Each reference covers install, env vars, setup snippet, and gotchas specific to that framework. The setup is rarely identical across frameworks — picking the wrong pattern (e.g. using `@traceable` when the framework has native OTel) creates duplicate/missing spans.

**Decision order:**
1. Framework has a dedicated reference below → use it
2. Framework has native OpenTelemetry but no dedicated reference → `references/otel.md`
3. No framework, or unsupported framework → `references/traceable.md`
4. Cannot run a LangSmith SDK at all → `references/api.md` (last resort)

**Routing table:**

| If you're tracing… | Read |
|---|---|
| OpenAI / Azure OpenAI / Anthropic / any plain LLM client | `references/traceable.md` |
| AutoGen | `references/autogen.md` |
| CrewAI | `references/crewai.md` |
| Google ADK | `references/google-adk.md` |
| Google Gemini (`google-genai` SDK directly) | `references/google-gemini.md` |
| Instructor (structured outputs) | `references/instructor.md` |
| LiveKit Agents (voice AI) | `references/livekit.md` |
| Mastra (TypeScript) | `references/mastra.md` |
| Microsoft Agent Framework | `references/microsoft-agent-framework.md` |
| Mistral | `references/mistral.md` |
| n8n (self-hosted) | `references/n8n.md` |
| OpenAI Agents SDK | `references/openai-agents-sdk.md` |
| OpenCode | `references/opencode.md` |
| OpenAI Codex CLI | `references/codex.md` |
| Pipecat (voice AI) | `references/pipecat.md` |
| PydanticAI | `references/pydantic-ai.md` |
| Semantic Kernel | `references/semantic-kernel.md` |
| Strands Agents | `references/strands-agents.md` |
| Temporal workflows (Go/Python/TS) | `references/temporal.md` |
| Vercel AI SDK | `references/vercel-ai-sdk.md` |
| Any other framework with native OTel | `references/otel.md` |
| Multi-backend OTel fan-out | `references/otel.md` (Collector section) |
| Raw REST (no SDK available) | `references/api.md` |

If the framework you need isn't listed here, check `references/` — new integrations are added there, not inline.
</trace_other_frameworks>

<traces_vs_runs>
Use the `langsmith` CLI to query trace data.

**Understanding the difference is critical:**

- **Trace** = A complete execution tree (root run + all child runs). A trace represents one full agent invocation with all its LLM calls, tool calls, and nested operations.
- **Run** = A single node in the tree (one LLM call, one tool call, etc.)

**Generally, query traces first** — they provide complete context and preserve hierarchy needed for trajectory analysis and dataset generation.
</traces_vs_runs>

<command_structure>
Two command groups with consistent behavior:

```
langsmith
├── trace (operations on trace trees - USE THIS FIRST)
│   ├── list    - List traces (filters apply to root run)
│   ├── get     - Get single trace with full hierarchy
│   └── export  - Export traces to JSONL files (one file per trace)
│
├── run (operations on individual runs - for specific analysis)
│   ├── list    - List runs (flat, filters apply to any run)
│   ├── get     - Get single run
│   └── export  - Export runs to single JSONL file (flat)
│
├── dataset (dataset operations)
│   ├── list    - List datasets
│   ├── get     - Get dataset details
│   ├── create  - Create empty dataset
│   ├── delete  - Delete dataset
│   ├── export  - Export dataset to file
│   └── upload  - Upload local JSON as dataset
│
├── example (example operations)
│   ├── list    - List examples in a dataset
│   ├── create  - Add example to a dataset
│   └── delete  - Delete an example
│
├── evaluator (evaluator operations)
│   ├── list    - List evaluators
│   ├── upload  - Upload evaluator
│   └── delete  - Delete evaluator
│
├── experiment (experiment operations)
│   ├── list    - List experiments
│   └── get     - Get experiment results
│
├── thread (thread operations)
│   ├── list    - List conversation threads
│   └── get     - Get thread details
│
└── project (project operations)
    └── list    - List tracing projects
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
Query traces using the `langsmith` CLI. Commands are language-agnostic.

```bash
# List recent traces (most common operation)
langsmith trace list --limit 10 --project my-project

# List traces with metadata (timing, tokens, costs)
langsmith trace list --limit 10 --include-metadata

# Filter traces by time
langsmith trace list --last-n-minutes 60
langsmith trace list --since 2025-01-20T10:00:00Z

# Get specific trace with full hierarchy
langsmith trace get <trace-id>

# List traces and show hierarchy inline
langsmith trace list --limit 5 --show-hierarchy

# Export traces to JSONL (one file per trace, includes all runs)
langsmith trace export ./traces --limit 20 --full

# Filter traces by performance
langsmith trace list --min-latency 5.0 --limit 10    # Slow traces (>= 5s)
langsmith trace list --error --last-n-minutes 60     # Failed traces

# List specific run types (flat list)
langsmith run list --run-type llm --limit 20
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
# Filter traces by feedback score using raw LangSmith query
langsmith trace list --filter 'and(eq(feedback_key, "correctness"), gte(feedback_score, 0.8))'
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
