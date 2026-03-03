---
name: langsmith-dataset-js
description: Use this skill for questions about creating test or evaluation datasets for agents. Covers dataset types (final_response, single_step, trajectory, RAG), uploading to LangSmith, and managing evaluation data.
---

<oneliner>
Create, manage, and upload evaluation datasets to LangSmith for testing and validation.
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
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

Export traces first, then process them into dataset format:

```bash
# 1. Export traces to JSONL files
langsmith trace export ./traces --project my-project --limit 20 --full
```

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

```typescript
import { Client } from "langsmith";

const client = new Client();

// Create dataset and add examples
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

<querying_traces>
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
</querying_traces>

<query>
```bash
# List all datasets
langsmith dataset list

# View dataset details
langsmith dataset get "Skills: Trajectory"

# List examples in a dataset
langsmith example list --dataset "Skills: Trajectory" --limit 5

# Export to local file
langsmith dataset export "Skills: Final Response" /tmp/exported.json --limit 100

# Delete a dataset
langsmith dataset delete "Old Dataset"
```
</query>

<example_workflow>
Complete workflow from exported traces to LangSmith datasets:

```bash
# 1. Export traces to JSONL files
langsmith trace export ./traces --project my-project --limit 20 --full
```

```typescript
// 2. Process traces into dataset (e.g., trajectory)
import { readFileSync, writeFileSync, readdirSync } from "fs";
import { join } from "path";

interface Run {
  run_id: string;
  trace_id: string;
  name: string;
  run_type: string;
  parent_run_id: string | null;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
}

const examples: Array<{inputs: Record<string, any>, outputs: Record<string, any>}> = [];
const files = readdirSync("./traces").filter(f => f.endsWith(".jsonl"));

for (const file of files) {
  const lines = readFileSync(join("./traces", file), "utf-8").trim().split("\n");
  const runs: Run[] = lines.map(line => JSON.parse(line));
  const root = runs.find(r => r.parent_run_id == null);
  if (!root) continue;

  const toolRuns = runs.filter(r => r.run_type === "tool");
  const trajectory = toolRuns.map(r => r.name);
  if (trajectory.length > 0 && root.inputs) {
    examples.push({
      trace_id: root.trace_id,
      inputs: root.inputs,
      outputs: { expected_trajectory: trajectory }
    });
  }
}

writeFileSync("/tmp/trajectory.json", JSON.stringify(examples, null, 2));
```

```bash
# 3. Upload to LangSmith
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory"

# 4. Verify
langsmith dataset get "Skills: Trajectory"
langsmith example list --dataset "Skills: Trajectory" --limit 3
```
</example_workflow>

</output>
