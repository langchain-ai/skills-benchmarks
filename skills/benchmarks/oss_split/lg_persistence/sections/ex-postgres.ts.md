Production-ready persistence:

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

// Create Postgres checkpointer
const checkpointer = PostgresSaver.fromConnString(
  "postgresql://user:pass@localhost/db"
);
await checkpointer.setup(); // only needed on first use to create tables

const graph = new StateGraph(State)
  .addNode("process", processNode)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "thread-1" } };
const result = await graph.invoke({ data: "test" }, config);
```
