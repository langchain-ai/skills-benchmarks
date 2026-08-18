HITL requires a checkpointer - always add `MemorySaver()` or another persistence backend.

Add checkpointer to enable HITL.

```typescript
// Problem: No checkpointer
const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  middleware: [humanInTheLoopMiddleware({...})],  // Error!
});

// Solution: Always add checkpointer
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required
  middleware: [humanInTheLoopMiddleware({...})],
});
```
