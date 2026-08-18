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
