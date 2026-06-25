PostgreSQL for production:

```typescript
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";

// Use PostgreSQL for production
const store = await PostgresStore.fromConnString(
  "postgresql://user:pass@localhost/db"
);

const graph = builder.compile({
  checkpointer,
  store,
});
```
