Emit custom data via writer:

```typescript
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const myNode = async (state, config: LangGraphRunnableConfig) => {
  const writer = config.writer;

  // Emit custom updates
  writer?.("Processing step 1...");
  // Do work
  writer?.("Processing step 2...");
  // More work
  writer?.("Complete!");

  return { result: "done" };
};

const graph = new StateGraph(State)
  .addNode("work", myNode)
  .compile();

for await (const chunk of await graph.stream(
  { data: "test" },
  { streamMode: "custom" }
)) {
  console.log(chunk);  // "Processing step 1...", etc.
}
```
