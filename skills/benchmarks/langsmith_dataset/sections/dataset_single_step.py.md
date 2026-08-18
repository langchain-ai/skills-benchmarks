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
