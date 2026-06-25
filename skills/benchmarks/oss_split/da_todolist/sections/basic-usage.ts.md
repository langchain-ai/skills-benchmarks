Agent uses write_todos for complex tasks:

```typescript
import { createDeepAgent } from "deepagents";

// TodoListMiddleware is included by default
const agent = await createDeepAgent({});

// Agent will automatically use write_todos for complex tasks
const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Create a TypeScript web scraper that extracts product data, stores it in a database, and generates a report."
  }]
});
```
