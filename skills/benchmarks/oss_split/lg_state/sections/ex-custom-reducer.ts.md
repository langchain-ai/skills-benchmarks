Custom reducer to merge objects:

```typescript
import { StateSchema, ReducedValue, START, END, StateGraph } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  metadata: new ReducedValue(
    z.record(z.string(), z.any()).default(() => ({})),
    {
      inputSchema: z.record(z.string(), z.any()),
      reducer: (current, update) => ({ ...current, ...update }),
    }
  ),
  data: z.string(),
});

const updateMetadata = async (state: typeof State.State) => {
  return { metadata: { timestamp: "2024-01-01" } };
};

const graph = new StateGraph(State)
  .addNode("update", updateMetadata)
  .addEdge(START, "update")
  .addEdge("update", END)
  .compile();

const result = await graph.invoke({
  metadata: { user: "alice" },
  data: "test",
});
// metadata is merged: { user: "alice", timestamp: "2024-01-01" }
```
