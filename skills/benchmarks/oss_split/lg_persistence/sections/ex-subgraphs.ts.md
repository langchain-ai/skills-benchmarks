Parent checkpointer propagates to subgraphs:

```typescript
import { MemorySaver, StateGraph, START } from "@langchain/langgraph";

// Only parent graph needs checkpointer
const subgraphNode = async (state) => ({ data: "subgraph" });

const subgraph = new StateGraph(State)
  .addNode("process", subgraphNode)
  .addEdge(START, "process")
  .compile();  // No checkpointer needed

// Parent graph with checkpointer
const checkpointer = new MemorySaver();

const parent = new StateGraph(State)
  .addNode("subgraph", subgraph)
  .addEdge(START, "subgraph")
  .compile({ checkpointer });  // Propagates to subgraph
```
