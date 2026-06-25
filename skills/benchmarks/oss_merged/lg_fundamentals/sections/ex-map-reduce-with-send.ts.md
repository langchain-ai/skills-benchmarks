Map items to Send objects for parallel execution.
```typescript
import { StateGraph, StateSchema, START, END, Send, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: z.array(z.string()),
  results: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (current, update) => current.concat(update)
  }),
});

const fanOut = (state: typeof State.State) =>
  state.items.map((item) => new Send("worker", { item }));

const worker = async (state: { item: string }) =>
  ({ results: [`Processed: ${state.item}`] });

const graph = new StateGraph(State)
  .addNode("worker", worker)
  .addConditionalEdges(START, fanOut, ["worker"])
  .addEdge("worker", END)
  .compile();
// invoke({ items: ["a", "b", "c"] }) -> results: ["Processed: a", "Processed: b", "Processed: c"]
```
