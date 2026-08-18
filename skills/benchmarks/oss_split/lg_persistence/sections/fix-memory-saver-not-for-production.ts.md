Use persistent storage in production:

```typescript
// WRONG - Data lost on restart
const checkpointer = new MemorySaver();  // In-memory only!

// CORRECT - Use persistent storage
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = PostgresSaver.fromConnString("postgresql://...");
await checkpointer.setup(); // only needed on first use to create tables
```
