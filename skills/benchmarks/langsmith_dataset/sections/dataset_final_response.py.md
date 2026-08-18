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
