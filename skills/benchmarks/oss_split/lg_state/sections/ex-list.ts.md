Append items with concat reducer:

```typescript
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      inputSchema: z.array(z.string()),
      reducer: (current, update) => current.concat(update),
    }
  ),
});

const addItems = async (state: typeof State.State) => {
  return { items: ["new_item"] };
};

const graph = new StateGraph(State)
  .addNode("add", addItems)
  .addEdge(START, "add")
  .addEdge("add", END)
  .compile();

const result = await graph.invoke({ items: ["old1", "old2"] });
console.log(result.items);  // ['old1', 'old2', 'new_item']
```
