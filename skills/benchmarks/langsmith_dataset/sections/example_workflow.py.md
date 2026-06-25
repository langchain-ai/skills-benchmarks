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
