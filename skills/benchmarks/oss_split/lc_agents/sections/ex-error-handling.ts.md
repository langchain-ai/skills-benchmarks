Custom error handling middleware:

```typescript
import { createAgent, createMiddleware } from "langchain";

// Custom error handling middleware
const errorHandler = createMiddleware({
  name: "ErrorHandler",
  wrapToolCall: async (request, handler) => {
    try {
      return await handler(request);
    } catch (error) {
      return {
        ...request.toolCall,
        content: `Tool error: ${error.message}`,
      };
    }
  },
});

const agent = createAgent({
  model: "gpt-4.1",
  tools: [riskyTool],
  middleware: [errorHandler],
});
```
