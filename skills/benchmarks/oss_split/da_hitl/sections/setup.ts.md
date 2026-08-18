Configure which tools require approval:

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: {
    write_file: true,  // All decisions allowed
    execute_sql: { allowedDecisions: ["approve", "reject"] },  // No editing
    read_file: false,  // No interrupts
  },
  checkpointer: new MemorySaver()  // REQUIRED
});
```
