---
name: langsmith-dataset-py
description: Use this skill for questions about creating test or evaluation datasets for agents. Covers dataset types (final_response, single_step, trajectory, RAG), uploading to LangSmith, and managing evaluation data.
---

<oneliner>
Create, manage, and upload evaluation datasets to LangSmith for testing and validation.
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_PROJECT=your-project-name                   # Check this to know which project has traces
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
```

**IMPORTANT:** Always check the environment variables or `.env` file for `LANGSMITH_PROJECT` before querying or interacting with LangSmith. This tells you which project contains the relevant traces and data. If the LangSmith project is not available, use your best judgement to identify the right one.

Python Dependencies
```bash
pip install langsmith
```

CLI Tool

```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

<input_format>
Datasets are built from traces exported in **JSONL format** (one run per line).

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
| `inputs` | Run inputs (required for dataset creation) |
| `outputs` | Run outputs (required for dataset creation) |

**Important:** You MUST have inputs and outputs to create datasets correctly.

**Before creating datasets, verify your traces exist:**
- Check that JSONL files exist in the output directory
- Confirm traces have both `inputs` and `outputs` populated
- Inspect the trace hierarchy to understand the structure
</input_format>

<usage>
Use the `langsmith` CLI to manage datasets and examples.

### Dataset Commands

- `langsmith dataset list` - List datasets in LangSmith
- `langsmith dataset get <name-or-id>` - View dataset details
- `langsmith dataset create --name <name>` - Create a new empty dataset
- `langsmith dataset delete <name-or-id>` - Delete a dataset
- `langsmith dataset export <name-or-id> <output-file>` - Export dataset to local JSON file
- `langsmith dataset upload <file> --name <name>` - Upload a local JSON file as a dataset

### Example Commands

- `langsmith example list --dataset <name>` - List examples in a dataset
- `langsmith example create --dataset <name> --inputs <json>` - Add an example
- `langsmith example delete <example-id>` - Delete an example

### Experiment Commands

- `langsmith experiment list --dataset <name>` - List experiments for a dataset
- `langsmith experiment get <name>` - View experiment results

**IMPORTANT - Safety Prompts:**
- The CLI prompts for confirmation before destructive operations
- **If you are running with user input:** ALWAYS wait for user input; NEVER use `--yes` unless the user explicitly requests it
- **If you are running non-interactively:** Use `--yes` to skip confirmation prompts
</usage>

<extraction_priority>
When extracting inputs/outputs from traces for dataset creation, use this priority:

1. **User-specified fields** (custom extraction logic)
2. **Messages array** (LangChain/OpenAI format)
3. **Common fields** (inputs: query, input, question, message, prompt, text; outputs: answer, output, response, result)
4. **Raw dict** (fallback)
</extraction_priority>

<trace_hierarchy>
Traces have depth levels based on parent-child relationships:

```
Depth 0: Root agent (e.g., "LangGraph")
  +-- Depth 1: Middleware/chains (model, tools, SummarizationMiddleware)
  |     +-- Depth 2: Tool calls (sql_db_query, retriever, etc.)
  |     +-- Depth 2: LLM calls (ChatOpenAI, ChatAnthropic)
  +-- Depth 3+: Nested subagent calls
```
</trace_hierarchy>

<dataset_types_overview>
Common evaluation dataset types:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior. Use run name to target a node.
- **trajectory** - Tool call sequence. Tests execution path. Use depth to control extraction.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
</dataset_types_overview>

<dataset_final_response>
Full conversation with expected output - tests complete agent behavior.

Extract root run inputs/outputs from each trace:

```python
import json
from pathlib import Path

examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    if root and root.get("inputs") and root.get("outputs"):
        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": root["inputs"],
            "outputs": root["outputs"]
        })

with open("/tmp/final_response.json", "w") as f:
    json.dump(examples, f, indent=2)
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"email_content": "..."},
  "outputs": {"expected_response": "The response text..."}
}
```

**Important:** Always use the root run (parent_run_id is null) for final response to avoid intermediate tool outputs.
</dataset_final_response>

<dataset_single_step>
Single node inputs/outputs - tests any specific node's behavior. **Supports multiple occurrences per trace** to capture conversation evolution.

```python
import json
from pathlib import Path

target_name = "model"  # Target node name
examples = []

for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    matching = [r for r in runs if r.get("name") == target_name]
    for i, run in enumerate(matching):
        if run.get("inputs") and run.get("outputs"):
            examples.append({
                "trace_id": run.get("trace_id"),
                "inputs": run["inputs"],
                "outputs": run["outputs"],
                "metadata": {"node_name": target_name, "occurrence": i + 1}
            })

with open("/tmp/single_step.json", "w") as f:
    json.dump(examples, f, indent=2)
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"email_content": "..."},
  "outputs": {"expected_output": {"category": "URGENT", "confidence": 0.95}},
  "metadata": {"node_name": "classify_email", "occurrence": 1}
}
```

**Key Features:**
- `node_name` identifies which node was extracted
- `occurrence` tracks which invocation (1st, 2nd, 3rd, etc.)
- Later occurrences have more conversation history - tests context handling

**Common targets:**
- `model` (depth 1) - LLM invocations with growing context
- `tools` (depth 1) - Tool execution chain
- Any custom node name
</dataset_single_step>

<dataset_trajectory>
Tool call sequence - tests execution path with configurable depth.

```python
import json
from pathlib import Path

examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    if not root:
        continue

    # Build parent-child map for depth calculation
    by_id = {r["run_id"]: r for r in runs}
    tool_runs = [r for r in runs if r.get("run_type") == "tool"]

    trajectory = [r["name"] for r in tool_runs]
    if trajectory and root.get("inputs"):
        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": root["inputs"],
            "outputs": {"expected_trajectory": trajectory}
        })

with open("/tmp/trajectory.json", "w") as f:
    json.dump(examples, f, indent=2)
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
- All levels = includes subagent tool calls
- Depth 2 = root + 2 levels (typical for capturing all main tools)
- Tool calls are typically at depth 2 in LangGraph/DeepAgents architecture

**Note:** Filter by `run_type="tool"` to get tool calls. Add depth filtering by computing parent chain length if needed.
</dataset_trajectory>

<dataset_rag>
Question/chunks/answer - tests retrieval quality. Only matches runs with `run_type="retriever"`.

```python
import json
from pathlib import Path

examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    retrievers = [r for r in runs if r.get("run_type") == "retriever"]

    if not root or not retrievers:
        continue

    for ret in retrievers:
        chunks = ret.get("outputs", {})
        # Extract page_content from LangChain Documents if present
        if isinstance(chunks, dict) and "documents" in chunks:
            chunks = [d.get("page_content", str(d)) for d in chunks["documents"]]

        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": {"question": root["inputs"].get("query", "")},
            "outputs": {
                "answer": root.get("outputs", {}).get("output", ""),
                "retrieved_chunks": chunks,
            }
        })

with open("/tmp/rag_dataset.json", "w") as f:
    json.dump(examples, f, indent=2)
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"question": "How do I..."},
  "outputs": {
    "answer": "The answer is...",
    "retrieved_chunks": ["Chunk 1", "Chunk 2"]
  }
}
```

For custom retriever names, filter by `name` instead of `run_type`.
</dataset_rag>

<upload>
```bash
# Upload local JSON file as a dataset
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory"

# Create empty dataset and add examples individually
langsmith dataset create --name "Skills: Final Response"
langsmith example create --dataset "Skills: Final Response" \
  --inputs '{"query": "test"}' \
  --outputs '{"answer": "result"}'
```

Or upload using the SDK:

```python
from langsmith import Client

client = Client()

dataset = client.create_dataset("Skills: Trajectory", description="Trajectory evaluation")
client.create_examples(
    inputs=[ex["inputs"] for ex in examples],
    outputs=[ex["outputs"] for ex in examples],
    dataset_name="Skills: Trajectory",
)
```
</upload>

<query>
```bash
# List all datasets
langsmith dataset list

# View dataset details
langsmith dataset get "Skills: Trajectory"

# List examples
langsmith example list --dataset "Skills: Trajectory" --limit 5

# Export from LangSmith to local
langsmith dataset export "Skills: Final Response" /tmp/exported.json --limit 100

# View experiments
langsmith experiment list --dataset "Skills: Trajectory"
```
</query>

<tips>
1. **Export successful traces first** - Use recent successful runs for baseline datasets
2. **Use time windows when exporting** - `--last-n-minutes 1440` for last 24 hours of data
3. **Verify exports have I/O** - Check that `inputs` and `outputs` are populated before processing
4. **Match depth to needs** - Depth 2 typically captures all main tool calls in LangGraph
5. **Iterative refinement** - Process small batches (5-20 traces) first, validate, then scale up
6. **Review before upload** - Inspect generated JSON before uploading to LangSmith
7. **Use the SDK for complex logic** - CLI is best for simple CRUD; SDK for programmatic dataset creation
</tips>

<example_workflow>
Complete workflow from exported traces to LangSmith datasets:

```bash
# 1. Export traces to JSONL files
langsmith trace export ./traces --project my-project --limit 20 --full
```

```python
# 2. Process traces into datasets (see dataset type sections above)
import json
from pathlib import Path

# Example: Create trajectory dataset
examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    if not root:
        continue
    tool_runs = [r for r in runs if r.get("run_type") == "tool"]
    trajectory = [r["name"] for r in tool_runs]
    if trajectory and root.get("inputs"):
        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": root["inputs"],
            "outputs": {"expected_trajectory": trajectory}
        })

with open("/tmp/trajectory.json", "w") as f:
    json.dump(examples, f, indent=2)
```

```bash
# 3. Upload to LangSmith
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory"

# 4. Verify
langsmith dataset get "Skills: Trajectory"
langsmith example list --dataset "Skills: Trajectory" --limit 3

# 5. Check experiments
langsmith experiment list --dataset "Skills: Trajectory"
```
</example_workflow>

<troubleshooting>
**Dataset upload fails:**
- Verify LANGSMITH_API_KEY is set
- Check JSON file is valid: array of objects with `inputs` key
- Dataset name must be unique, or delete existing first

**Empty dataset after upload:**
- Verify JSON file contains an array of objects with `inputs` key
- Check file isn't empty: `langsmith example list --dataset "Name"`

**No trajectory data in traces:**
- Tools might be at different depth - check trace hierarchy
- Verify tool calls exist in your exported JSONL files
- Use `langsmith trace get <id>` to inspect trace structure

**Too many single_step examples:**
- Sample N occurrences per trace to limit dataset size
- Reduces dataset size while maintaining diversity

**No RAG data:**
- RAG only matches `run_type="retriever"`
- For custom retriever names, filter by `name` instead

**Export has no data:**
- Ensure traces were exported with `--full` flag to include inputs/outputs
- Verify traces have both `inputs` and `outputs` populated
</troubleshooting>

</output>
