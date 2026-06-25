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
