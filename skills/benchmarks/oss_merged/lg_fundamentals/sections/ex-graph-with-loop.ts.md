Return END from conditional function to terminate loop.
```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number().default(0),
  maxIterations: z.number(),
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };
};

const shouldContinue = (state: typeof State.State) => {
  if (state.count >= state.maxIterations) return END;
  return "increment";
};

const graph = new StateGraph(State)
  .addNode("increment", increment)
  .addEdge(START, "increment")
  .addConditionalEdges("increment", shouldContinue)
  .compile();

const result = await graph.invoke({ count: 0, maxIterations: 5 });
console.log(result.count);  // 5
```
