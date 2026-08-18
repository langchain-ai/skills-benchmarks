Update only specific fields:

```typescript
import { StateSchema, StateGraph, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  field1: z.string(),
  field2: z.string(),
  field3: z.string(),
});

const updateField1 = async (state: typeof State.State) => {
  // Only update field1, others unchanged
  return { field1: "updated" };
};

const updateField2 = async (state: typeof State.State) => {
  // Only update field2
  return { field2: "also updated" };
};

const graph = new StateGraph(State)
  .addNode("node1", updateField1)
  .addNode("node2", updateField2)
  .addEdge(START, "node1")
  .addEdge("node1", "node2")
  .addEdge("node2", END)
  .compile();

const result = await graph.invoke({
  field1: "original1",
  field2: "original2",
  field3: "original3",
});
// field1: "updated", field2: "also updated", field3: "original3"
```
