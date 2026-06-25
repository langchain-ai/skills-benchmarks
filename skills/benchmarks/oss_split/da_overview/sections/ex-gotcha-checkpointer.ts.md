Provide checkpointer when using HITL:

```typescript
// This will error if interruptOn is set
const agent = await createDeepAgent({
  interruptOn: { write_file: true }
});

// Checkpointer is required
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
