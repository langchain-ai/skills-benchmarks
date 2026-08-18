Use persistent backend in production:

```typescript
// WRONG - Data lost on restart
const store = new InMemoryStore();  // Memory only!

// CORRECT - Use persistent backend
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";
const store = await PostgresStore.fromConnString("postgresql://...");
```
