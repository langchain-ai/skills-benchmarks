Compile with checkpointer and breakpoints:

```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("nodeA", nodeA)
  .addEdge(START, "nodeA")
  .addEdge("nodeA", END)
  .compile({
    checkpointer,                    // Enable persistence
    interruptBefore: ["nodeA"],      // Breakpoint before node
    interruptAfter: ["nodeA"],       // Breakpoint after node
  });
```
