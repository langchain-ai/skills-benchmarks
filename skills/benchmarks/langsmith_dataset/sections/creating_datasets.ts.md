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
