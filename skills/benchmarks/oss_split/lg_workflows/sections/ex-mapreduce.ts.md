Parallel processing with aggregation:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const MapReduceState = new StateSchema({
  documents: z.array(z.string()),
  summaries: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  finalSummary: z.string().optional(),
});

const mapDocuments = (state: typeof MapReduceState.State) => {
  return state.documents.map(doc => new Send("summarize", { doc }));
};

const summarize = async (state: { doc: string }) => {
  const summary = `Summary of: ${state.doc.slice(0, 50)}...`;
  return { summaries: [summary] };
};

const reduce = async (state: typeof MapReduceState.State) => {
  const finalSummary = state.summaries.join(" | ");
  return { finalSummary };
};

const graph = new StateGraph(MapReduceState)
  .addNode("summarize", summarize)
  .addNode("reduce", reduce)
  .addConditionalEdges(START, mapDocuments, ["summarize"])
  .addEdge("summarize", "reduce")
  .addEdge("reduce", END)
  .compile();

const result = await graph.invoke({
  documents: ["Doc 1 content...", "Doc 2 content...", "Doc 3 content..."],
});
```
