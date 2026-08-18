File-based persistence for local development:

```typescript
import { SqliteSaver } from "@langchain/langgraph-checkpoint-sqlite";

// Create SQLite checkpointer
const checkpointer = SqliteSaver.fromConnString("checkpoints.db");

const graph = new StateGraph(State)
  .addNode("process", processNode)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile({ checkpointer });

// Use with thread_id
const config = { configurable: { thread_id: "user-123" } };
const result = await graph.invoke({ data: "test" }, config);
```
