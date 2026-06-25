Command combining state and routing:

```typescript
import { StateGraph, StateSchema, Command, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number(),
  result: z.string(),
});

const nodeA = async (state: typeof State.State) => {
  const newCount = state.count + 1;

  if (newCount > 5) {
    // Go to nodeC
    return new Command({
      update: { count: newCount, result: "Going to C" },
      goto: "nodeC"
    });
  } else {
    // Go to nodeB
    return new Command({
      update: { count: newCount, result: "Going to B" },
      goto: "nodeB"
    });
  }
};

const nodeB = async (state: typeof State.State) => {
  return { result: `B executed, count=${state.count}` };
};

const nodeC = async (state: typeof State.State) => {
  return { result: `C executed, count=${state.count}` };
};

const graph = new StateGraph(State)
  .addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] })  // Specify possible routes
  .addNode("nodeB", nodeB)
  .addNode("nodeC", nodeC)
  .addEdge(START, "nodeA")
  .addEdge("nodeB", END)
  .addEdge("nodeC", END)
  .compile();

const result1 = await graph.invoke({ count: 0 });
console.log(result1.result);  // "B executed, count=1"

const result2 = await graph.invoke({ count: 5 });
console.log(result2.result);  // "C executed, count=6"
```
