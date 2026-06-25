Route to multiple sources:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const RouterState = new StateSchema({
  query: z.string(),
  sources: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  final: z.string().optional(),
});

const classify = async (state: typeof RouterState.State) => {
  const query = state.query.toLowerCase();
  const sources: string[] = [];

  if (query.includes("code")) sources.push("github");
  if (query.includes("doc")) sources.push("notion");
  if (query.includes("message")) sources.push("slack");

  return { sources };
};

const routeToSources = (state: typeof RouterState.State) => {
  return state.sources.map(source => new Send(source, { query: state.query }));
};

const queryGithub = async (state: { query: string }) => {
  return { results: [`GitHub: ${state.query}`] };
};

const queryNotion = async (state: { query: string }) => {
  return { results: [`Notion: ${state.query}`] };
};

const querySlack = async (state: { query: string }) => {
  return { results: [`Slack: ${state.query}`] };
};

const synthesize = async (state: typeof RouterState.State) => {
  return { final: state.results.join(" + ") };
};

const graph = new StateGraph(RouterState)
  .addNode("classify", classify)
  .addNode("github", queryGithub)
  .addNode("notion", queryNotion)
  .addNode("slack", querySlack)
  .addNode("synthesize", synthesize)
  .addEdge(START, "classify")
  .addConditionalEdges("classify", routeToSources, ["github", "notion", "slack"])
  .addEdge("github", "synthesize")
  .addEdge("notion", "synthesize")
  .addEdge("slack", "synthesize")
  .addEdge("synthesize", END)
  .compile();
```
