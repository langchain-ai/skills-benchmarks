Default StateBackend stores files ephemerally within a thread.
```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent();  // Default: StateBackend
const result = await agent.invoke({
  messages: [{ role: "user", content: "Write notes to /draft.txt" }]
}, { configurable: { thread_id: "thread-1" } });
// /draft.txt is lost when thread ends
```
