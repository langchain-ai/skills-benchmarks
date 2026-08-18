Custom middleware with conditional interrupts.

```typescript
import { createMiddleware } from "langchain";

const customHITL = createMiddleware({
  name: "CustomHITL",
  wrapToolCall: async (toolCall, handler, runtime) => {
    // Custom logic to decide if interrupt needed
    if (toolCall.name === "database_write") {
      const value = toolCall.args.value;

      if (value > 1000) {
        // Interrupt for large values
        const decision = await runtime.interrupt({
          toolCall,
          reason: "Large database write requires approval",
        });

        if (decision.type === "approve") {
          return await handler(toolCall);
        } else if (decision.type === "edit") {
          return await handler({ ...toolCall, args: decision.args });
        } else {
          throw new Error(decision.feedback || "Rejected");
        }
      }
    }

    // No interrupt needed
    return await handler(toolCall);
  },
});
```
