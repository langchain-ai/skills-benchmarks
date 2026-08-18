Router with conditional branching:

```typescript
import { StateGraph, StateSchema, ConditionalEdgeRouter, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  query: z.string(),
  route: z.string(),
  result: z.string().optional(),
});

const classify = async (state: typeof State.State) => {
  if (state.query.toLowerCase().includes("weather")) {
    return { route: "weather" };
  }
  return { route: "general" };
};

const weatherNode = async (state: typeof State.State) => {
  return { result: "Sunny, 72°F" };
};

const generalNode = async (state: typeof State.State) => {
  return { result: "General response" };
};

// Router function
const routeQuery: ConditionalEdgeRouter<typeof State, "weather" | "general"> = (state) => {
  return state.route as "weather" | "general";
};

const graph = new StateGraph(State)
  .addNode("classify", classify)
  .addNode("weather", weatherNode)
  .addNode("general", generalNode)
  .addEdge(START, "classify")
  // Conditional edge based on state
  .addConditionalEdges(
    "classify",
    routeQuery,
    ["weather", "general"]  // Possible destinations
  )
  .addEdge("weather", END)
  .addEdge("general", END)
  .compile();

const result = await graph.invoke({ query: "What's the weather?" });
```
