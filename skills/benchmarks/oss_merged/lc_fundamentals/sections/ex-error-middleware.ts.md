Catch and handle tool errors gracefully with custom middleware.
```typescript
import { createAgent, createMiddleware } from "langchain";

const errorHandler = createMiddleware({
  name: "ErrorHandler",
  wrapToolCall: async (request, handler) => {
    try {
      return await handler(request);
    } catch (error) {
      return {
        ...request.toolCall,
        content: `Tool error: ${error}. Please try a different approach.`,
      };
    }
  },
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [riskyTool],
  middleware: [errorHandler],
});
```
