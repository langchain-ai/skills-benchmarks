---
name: langsmith-dataset
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

JavaScript Dependencies
```bash
npm install langsmith
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
- **NEVER use `--yes` unless the user explicitly requests it**
</usage>

<dataset_types_overview>
Common evaluation dataset types:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior.
- **trajectory** - Tool call sequence. Tests execution path.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
</dataset_types_overview>

<creating_datasets>
## Creating Datasets

Export traces first, then process them into dataset format using code:

```bash
# 1. Export traces to JSONL files
langsmith trace export ./traces --project my-project --limit 20 --full
```

### Python

```python
import json
from pathlib import Path
from langsmith import Client

client = Client()

# 2. Process traces into dataset examples (e.g., final_response)
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

# 3. Save locally
with open("/tmp/dataset.json", "w") as f:
    json.dump(examples, f, indent=2)
```

### JavaScript

```typescript
import { Client } from "langsmith";
import { readFileSync, writeFileSync, readdirSync } from "fs";
import { join } from "path";

// 2. Process traces into dataset examples
const examples: Array<{inputs: Record<string, any>, outputs: Record<string, any>}> = [];
const files = readdirSync("./traces").filter(f => f.endsWith(".jsonl"));

for (const file of files) {
  const lines = readFileSync(join("./traces", file), "utf-8").trim().split("\n");
  const runs = lines.map(line => JSON.parse(line));
  const root = runs.find(r => r.parent_run_id == null);
  if (root?.inputs && root?.outputs) {
    examples.push({ trace_id: root.trace_id, inputs: root.inputs, outputs: root.outputs });
  }
}

// 3. Save locally
writeFileSync("/tmp/dataset.json", JSON.stringify(examples, null, 2));
```

### Upload to LangSmith

```bash
langsmith dataset upload /tmp/dataset.json --name "My Evaluation Dataset"
```

### Using the SDK Directly

**Python:**

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("My Dataset", description="Evaluation dataset")
client.create_examples(
    inputs=[{"query": "What is AI?"}, {"query": "Explain RAG"}],
    outputs=[{"answer": "AI is..."}, {"answer": "RAG is..."}],
    dataset_name="My Dataset",
)
```

**JavaScript:**

```typescript
import { Client } from "langsmith";

const client = new Client();
const dataset = await client.createDataset("My Dataset", {
  description: "Evaluation dataset",
});
await client.createExamples({
  inputs: [{ query: "What is AI?" }, { query: "Explain RAG" }],
  outputs: [{ answer: "AI is..." }, { answer: "RAG is..." }],
  datasetName: "My Dataset",
});
```
</creating_datasets>

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

<example_workflow>
Complete workflow from exported traces to LangSmith datasets:

```bash
# 1. Export traces to JSONL files
langsmith trace export ./traces --project my-project --limit 20 --full

# 2. Process traces into datasets (using Python/JS code)
# See "Creating Datasets" section above

# 3. Upload to LangSmith
langsmith dataset upload /tmp/final_response.json --name "Skills: Final Response"
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory"

# 4. Verify
langsmith dataset list
langsmith dataset get "Skills: Final Response"
langsmith example list --dataset "Skills: Final Response" --limit 3
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

**No RAG data:**
- RAG only matches `run_type="retriever"`
- For custom retriever names, filter by `name` instead

**Export has no data:**
- Ensure traces were exported with `--full` flag to include inputs/outputs
- Verify traces have both `inputs` and `outputs` populated
</troubleshooting>

</output>
