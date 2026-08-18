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
