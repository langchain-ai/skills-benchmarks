Simple state with partial updates:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  input: z.string(),
  processed: z.string(),
  count: z.number(),
});

const process = async (state: typeof State.State) => {
  return {
    processed: state.input.toUpperCase(),
    count: state.count + 1,
  };
};

const graph = new StateGraph(State)
  .addNode("process", process)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile();

const result = await graph.invoke({ input: "hello", count: 0 });
console.log(result);  // { input: 'hello', processed: 'HELLO', count: 1 }
```
