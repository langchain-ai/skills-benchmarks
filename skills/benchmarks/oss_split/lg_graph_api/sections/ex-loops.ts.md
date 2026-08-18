Loop with conditional exit:

```typescript
import { StateGraph, StateSchema, ConditionalEdgeRouter, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number(),
  maxIterations: z.number(),
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };
};

const shouldContinue: ConditionalEdgeRouter<typeof State, "increment"> = (state) => {
  if (state.count >= state.maxIterations) {
    return END;
  }
  return "increment";
};

const graph = new StateGraph(State)
  .addNode("increment", increment)
  .addEdge(START, "increment")
  .addConditionalEdges("increment", shouldContinue, ["increment", END])
  .compile();

const result = await graph.invoke({ count: 0, maxIterations: 5 });
console.log(result.count);  // 5
```
