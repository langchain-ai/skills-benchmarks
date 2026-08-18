Fan-out with Send API:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  final: z.string().optional(),
});

const fanOut = (state: typeof State.State) => {
  // Send each item to a worker node
  return state.items.map(item =>
    new Send("worker", { item })
  );
};

const worker = async (state: { item: string }) => {
  // Process a single item
  return { results: [`Processed: ${state.item}`] };
};

const aggregate = async (state: typeof State.State) => {
  // Combine results
  return { final: state.results.join(", ") };
};

const graph = new StateGraph(State)
  .addNode("worker", worker)
  .addNode("aggregate", aggregate)
  .addConditionalEdges(START, fanOut, ["worker"])
  .addEdge("worker", "aggregate")
  .addEdge("aggregate", END)
  .compile();

const result = await graph.invoke({ items: ["A", "B", "C"] });
console.log(result.final);  // "Processed: A, Processed: B, Processed: C"
```
