Use createAgent for full control:

```typescript
// You cannot remove TodoListMiddleware from createDeepAgent
// This won't remove TodoList
const agent = await createDeepAgent({ middleware: [] });  // TodoList still included

// If you need full control, use createAgent from LangChain
import { createAgent } from "langchain";

const agent2 = createAgent({
  model: "gpt-4.1",
  middleware: []  // No middleware at all
});
```
