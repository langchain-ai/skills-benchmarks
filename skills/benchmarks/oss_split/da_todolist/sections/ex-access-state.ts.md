Read todos from final state:

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});

const result = await agent.invoke(
  {
    messages: [{
      role: "user",
      content: "Create a data processing pipeline"
    }]
  },
  { configurable: { thread_id: "session-1" } }
);

// Access the todo list from the final state
const todos = result.todos || [];
for (const todo of todos) {
  console.log(`[${todo.status}] ${todo.content}`);
}
```
