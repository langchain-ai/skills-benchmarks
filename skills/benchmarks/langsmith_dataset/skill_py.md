---
name: langsmith-dataset-py
description: Use this skill for questions about creating test or evaluation datasets for agents. Covers generating datasets from exported trace files (final_response, single_step, trajectory, RAG types), uploading to LangSmith, and managing evaluation data.
---

<oneliner>
Auto-generate evaluation datasets from exported JSONL trace files for testing and validation.
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
```

CLI Tool

```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

<input_format>
Dataset generation requires traces exported in **JSONL format** (one run per line).

### Required Fields

Each line must be a JSON object with these fields:

```json
{"run_id": "...", "trace_id": "...", "name": "...", "run_type": "...", "parent_run_id": "...", "inputs": {...}, "outputs": {...}}
```

| Field | Description |
|-------|-------------|
| `run_id` | Unique identifier for this run |
| `trace_id` | Groups runs into traces (used for hierarchy reconstruction) |
| `name` | Run name (e.g., "model", "classify_email") |
| `run_type` | One of: chain, llm, tool, retriever |
| `parent_run_id` | Parent run ID (null for root) |
| `inputs` | Run inputs (required for dataset generation) |
| `outputs` | Run outputs (required for dataset generation) |

**Important:** You MUST have inputs and outputs to generate datasets correctly.

**Before generating datasets, verify your traces exist:**
- Check that JSONL files exist in the output directory
- Confirm traces have both `inputs` and `outputs` populated
- Inspect the trace hierarchy to understand the structure
</input_format>

<usage>
Use the `langsmith` CLI to generate and manage datasets.

### Commands

- `langsmith dataset generate` - Create evaluation datasets from exported trace files
- `langsmith dataset list` - List datasets in LangSmith
- `langsmith dataset get` - View dataset details
- `langsmith dataset export` - Export dataset to local file
- `langsmith dataset view-file` - View local dataset file
- `langsmith dataset structure` - Analyze dataset structure

### Common Flags

All dataset generation commands support:

- `--input <path>` - Input traces: directory of .jsonl files or single .jsonl file (required)
- `--type <type>` - Dataset type: final_response, single_step, trajectory, rag (required)
- `--output <path>` - Output file (.json or .csv) (required)
- `--input-fields` - Comma-separated input keys to extract (e.g., "query,question")
- `--output-fields` - Comma-separated output keys to extract (e.g., "answer,response")
- `--messages-only` - Only extract from messages arrays, skip other fields
- `--upload <name>` - Upload to LangSmith with this dataset name
- `--replace` - Overwrite existing file/dataset (will prompt for confirmation)
- `--yes` - Skip confirmation prompts (use with caution)

**IMPORTANT - Safety Prompts:**
- The CLI prompts for confirmation before deleting existing datasets with `--replace`
- **If you are running with user input:** ALWAYS wait for user input; NEVER use `--yes` unless the user explicitly requests it
- **If you are running non-interactively:** Use `--replace --yes` together to ensure proper replacement
</usage>

<extraction_priority>
When extracting inputs/outputs for dataset generation, the CLI uses this priority:

1. **User-specified fields** (`--input-fields`, `--output-fields`)
2. **Messages array** (LangChain/OpenAI format)
3. **Common fields** (inputs: query, input, question, message, prompt, text; outputs: answer, output, response, result)
4. **Raw dict** (fallback)
</extraction_priority>

<trace_hierarchy>
Traces have depth levels based on parent-child relationships:

```
Depth 0: Root agent (e.g., "LangGraph")
  ├── Depth 1: Middleware/chains (model, tools, SummarizationMiddleware)
  │     ├── Depth 2: Tool calls (sql_db_query, retriever, etc.)
  │     └── Depth 2: LLM calls (ChatOpenAI, ChatAnthropic)
  └── Depth 3+: Nested subagent calls
```
</trace_hierarchy>

<dataset_types_overview>
Use `--type <type>` flag with `langsmith dataset generate`:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior. Use `--run-name` to target a node.
- **trajectory** - Tool call sequence. Tests execution path. Use `--depth` to control depth.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
</dataset_types_overview>

<dataset_final_response>
Full conversation with expected output - tests complete agent behavior.

```bash
# Basic usage (raw inputs, extracted output)
langsmith dataset generate --input ./traces --type final_response --output /tmp/final_response.json

# Extract specific fields
langsmith dataset generate --input ./traces --type final_response \
  --input-fields "email_content" \
  --output-fields "response" \
  --output /tmp/final.json

# Messages only (ignore output dict keys)
langsmith dataset generate --input ./traces --type final_response \
  --messages-only \
  --output /tmp/final.json
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"email_content": "..."},
  "outputs": {"expected_response": "The response text..."}
}
```

With `--input-fields`, inputs become `{"expected_input": "extracted value"}`.

**Important:** Always checks root run first for final response to avoid intermediate tool outputs.
</dataset_final_response>

<dataset_single_step>
Single node inputs/outputs - tests any specific node's behavior. **Supports multiple occurrences per trace** to capture conversation evolution.

```bash
# Extract all occurrences (default)
langsmith dataset generate --input ./traces --type single_step \
  --run-name model \
  --output /tmp/single_step.json

# Sample 2 occurrences per trace
langsmith dataset generate --input ./traces --type single_step \
  --run-name model \
  --sample-per-trace 2 \
  --output /tmp/single_step_sampled.json

# Target specific tool
langsmith dataset generate --input ./traces --type single_step \
  --run-name classify_email \
  --output /tmp/classify.json
```

**Structure:**
```json
{
  "trace_id": "...",
  "run_id": "...",
  "node_name": "classify_email",
  "occurrence": 1,
  "inputs": {"email_content": "..."},
  "outputs": {"expected_output": {"category": "URGENT", "confidence": 0.95}}
}
```

**Key Features:**
- `node_name` at top level identifies which node was extracted
- `occurrence` field tracks which invocation (1st, 2nd, 3rd, etc.)
- Later occurrences have more conversation history → tests context handling
- `--sample-per-trace` randomly samples N occurrences per trace
- Use `--run-name` to target any node at any depth

**Common targets:**
- `model` (depth 1) - LLM invocations with growing context
- `tools` (depth 1) - Tool execution chain
- Any custom node name
</dataset_single_step>

<dataset_trajectory>
Tool call sequence - tests execution path with configurable depth.

```bash
# Include all tool calls (all depths)
langsmith dataset generate --input ./traces --type trajectory --output /tmp/trajectory_all.json

# Only tool calls up to depth 2
langsmith dataset generate --input ./traces --type trajectory \
  --depth 2 \
  --output /tmp/trajectory_depth2.json
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"query": "What are the top 3 genres?"},
  "outputs": {
    "expected_trajectory": [
      "sql_db_list_tables",
      "sql_db_schema",
      "sql_db_query_checker",
      "sql_db_query"
    ]
  }
}
```

**Depth Control:**
- Omit `--depth` = all levels (includes subagent tool calls)
- `--depth 2` = root + 2 levels (typical for capturing all main tools)
- `--depth 1` = often only middleware/chains, no actual tool calls
- `--depth 0` = root only (no tool calls)

**Note:** Tool calls are typically at depth 2 in LangGraph/DeepAgents architecture.
</dataset_trajectory>

<dataset_rag>
Question/chunks/answer - tests retrieval quality. Only matches runs with `run_type="retriever"`.

```bash
langsmith dataset generate --input ./traces --type rag --output /tmp/rag_ds.json
```

**Structure:**
```json
{
  "trace_id": "...",
  "question": "How do I...",
  "retrieved_chunks": "Chunk 1\n\nChunk 2",
  "answer": "The answer is...",
  "cited_chunks": "[\"Chunk 1\", \"Chunk 2\"]"
}
```

Extracts LangChain Documents (`page_content`) if present, otherwise returns raw outputs.
</dataset_rag>

<output_formats>
All dataset types support both JSON and CSV:
```bash
# JSON output (default)
langsmith dataset generate --input ./traces --type trajectory --output ds.json

# CSV output (use .csv extension)
langsmith dataset generate --input ./traces --type trajectory --output ds.csv
```
</output_formats>

<upload>
```bash
# Generate and upload in one command
langsmith dataset generate --input ./traces --type trajectory \
  --output /tmp/trajectory_ds.json \
  --upload "Skills: Trajectory"

# Use --replace to overwrite existing dataset
langsmith dataset generate --input ./traces --type final_response \
  --output /tmp/final.json \
  --upload "Skills: Final Response" \
  --replace
```
</upload>

<query>
```bash
# List all datasets
langsmith dataset list

# View dataset examples
langsmith dataset get "Skills: Trajectory" --limit 5

# View local file
langsmith dataset view-file /tmp/trajectory_ds.json --limit 3

# Analyze structure
langsmith dataset structure /tmp/trajectory_ds.json

# Export from LangSmith to local
langsmith dataset export "Skills: Final Response" /tmp/exported.json --limit 100
```
</query>

<tips>
1. **Export successful traces first** - Use recent successful runs for baseline datasets
2. **Use time windows when exporting** - `--last-n-minutes 1440` for last 24 hours of data
3. **Verify exports have I/O** - Check that `inputs` and `outputs` are populated before generating
4. **Sample for single_step** - Use `--sample-per-trace 2` to capture conversation evolution
5. **Match depth to needs** - `--depth 2` typically captures all main tool calls
6. **Review before upload** - Use `langsmith dataset view-file` to inspect first
7. **Iterative refinement** - Generate small batches (5-20) first, validate, then scale up
8. **Use `--replace` carefully** - Overwrites existing datasets, useful for iteration
</tips>

<example_workflow>
Complete workflow from exported traces to LangSmith datasets:

```bash
# Assuming traces are already exported to ./traces as JSONL files

# Generate all dataset types from exported traces
langsmith dataset generate --input ./traces --type final_response \
  --output /tmp/final.json \
  --upload "Skills: Final Response" --replace

langsmith dataset generate --input ./traces --type single_step \
  --run-name model \
  --sample-per-trace 2 \
  --output /tmp/model.json \
  --upload "Skills: Single Step (model)" --replace

langsmith dataset generate --input ./traces --type trajectory \
  --output /tmp/traj.json \
  --upload "Skills: Trajectory (all depths)" --replace

# 3. Review in LangSmith UI
# Visit https://smith.langchain.com → Datasets

# 4. Query locally if needed
langsmith dataset get "Skills: Final Response" --limit 3
```
</example_workflow>

<troubleshooting>
**"No valid traces found":**
- Ensure input path contains `.jsonl` files (not `.json`)
- Check files have required fields (trace_id, inputs, outputs)
- Verify traces have inputs and outputs populated

**Empty final_response outputs:**
- Check that root run has outputs
- Use `--output-fields` to target specific field
- Use `--messages-only` if output is in messages format

**No trajectory examples:**
- Tools might be at different depth - try removing `--depth` or use `--depth 2`
- Verify tool calls exist in your exported JSONL files

**Too many single_step examples:**
- Use `--sample-per-trace 2` to limit examples per trace
- Reduces dataset size while maintaining diversity

**No RAG data:**
- RAG only matches `run_type="retriever"`
- For custom retriever names, use `single_step --run-name <retriever>` instead

**Dataset upload fails:**
- Check dataset doesn't exist or use `--replace`
- Verify LANGSMITH_API_KEY is set
</troubleshooting>

