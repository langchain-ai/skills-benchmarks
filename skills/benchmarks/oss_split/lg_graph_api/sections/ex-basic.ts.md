Basic graph with static edges:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

// 1. Define state
const State = new StateSchema({
  input: z.string(),
  output: z.string(),
});

// 2. Define nodes
const processInput = async (state: typeof State.State) => {
  return { output: `Processed: ${state.input}` };
};

const finalize = async (state: typeof State.State) => {
  return { output: state.output.toUpperCase() };
};

// 3. Build graph
const graph = new StateGraph(State)
  .addNode("process", processInput)
  .addNode("finalize", finalize)
  .addEdge(START, "process")       // Entry point
  .addEdge("process", "finalize")  // Static edge
  .addEdge("finalize", END)        // Exit point
  .compile();

// 4. Execute
const result = await graph.invoke({ input: "hello" });
console.log(result.output);  // "PROCESSED: HELLO"
```
