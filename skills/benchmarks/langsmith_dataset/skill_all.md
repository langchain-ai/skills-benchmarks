---
name: langsmith-dataset
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

<dataset_types_overview>
Use `--type <type>` flag with the generate_datasets script:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior. Use `--run-name` to target a node.
- **trajectory** - Tool call sequence. Tests execution path. Use `--depth` to control depth.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
</dataset_types_overview>

<cli_usage>
## CLI Usage

```bash
# Basic usage (raw inputs, extracted output)
langsmith dataset generate --input ./traces --type final_response --output /tmp/final_response.json

# Extract specific fields
langsmith dataset generate --input ./traces --type final_response \
  --input-fields "email_content" \
  --output-fields "response" \
  --output /tmp/final.json

# Generate trajectory dataset
langsmith dataset generate --input ./traces --type trajectory --output /tmp/trajectory.json

# Generate and upload
langsmith dataset generate --input ./traces --type trajectory \
  --output /tmp/trajectory.json \
  --upload "Skills: Trajectory"

# Query datasets
langsmith dataset list
langsmith dataset get "Skills: Trajectory" --limit 5
langsmith dataset view-file /tmp/trajectory_ds.json --limit 3
```
</cli_usage>

<example_workflow>
Complete workflow from exported traces to LangSmith datasets:

```bash
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

# Query locally if needed
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

