Full state after each step:

```typescript
import { StateGraph, START, END } from "@langchain/langgraph";

const process = async (state) => ({  count: state.count + 1 });

const graph = new StateGraph(State)
  .addNode("process", process)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile();

// Stream full state after each step
for await (const chunk of await graph.stream(
  { count: 0 },
  { streamMode: "values" }
)) {
  console.log(chunk);  // { count: 0 }, then { count: 1 }
}
```
