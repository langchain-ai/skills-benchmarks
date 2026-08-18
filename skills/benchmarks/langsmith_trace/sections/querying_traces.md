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
langsmith trace export ./traces --limit 10 --include-io

# Filter traces by performance
langsmith trace list --min-latency 5.0 --limit 10    # Slow traces (>= 5s)
langsmith trace list --error --last-n-minutes 60     # Failed traces

# Export specific traces by ID
langsmith trace export ./traces --trace-ids abc123,def456 --full

# Stitch multiple JSONL files together
cat ./traces/*.jsonl > all_traces.jsonl

# --- RUNS (for specific analysis) ---

# List specific run types (flat list)
langsmith run list --run-type llm --limit 20         # LLM calls only
langsmith run list --name "ChatOpenAI" --limit 10    # By name pattern

# Get a specific run by ID
langsmith run get <run-id> --full

# Export LLM runs for analysis
langsmith run export ./llm_runs.jsonl --run-type llm --limit 100 --full
```
