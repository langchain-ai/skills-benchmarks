Fan-out with Send API:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const OrchestratorState = new StateSchema({
  tasks: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  summary: z.string().optional(),
});

const orchestrator = (state: typeof OrchestratorState.State) => {
  // Fan out tasks to workers
  return state.tasks.map(task => new Send("worker", { task }));
};

const worker = async (state: { task: string }) => {
  const result = `Completed: ${state.task}`;
  return { results: [result] };
};

const synthesize = async (state: typeof OrchestratorState.State) => {
  const summary = `Processed ${state.results.length} tasks`;
  return { summary };
};

const graph = new StateGraph(OrchestratorState)
  .addNode("worker", worker)
  .addNode("synthesize", synthesize)
  .addConditionalEdges(START, orchestrator, ["worker"])
  .addEdge("worker", "synthesize")
  .addEdge("synthesize", END)
  .compile();

const result = await graph.invoke({
  tasks: ["Task A", "Task B", "Task C"],
});
console.log(result.summary);  // "Processed 3 tasks"
```
