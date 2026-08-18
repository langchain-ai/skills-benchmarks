Use PostgresStore for production:

```typescript
// Lost on restart
const store = new InMemoryStore();

// Use persistent store for production
import { PostgresStore } from "@langchain/langgraph";
const store = new PostgresStore({ connectionString: "postgresql://..." });
```
