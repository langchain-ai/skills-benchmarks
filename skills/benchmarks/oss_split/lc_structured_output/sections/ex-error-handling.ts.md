Handle validation errors with try/catch.

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const StrictSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(120),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: StrictSchema,
});

try {
  const result = await agent.invoke({
    messages: [{ role: "user", content: "Email: invalid, Age: -5" }],
  });
} catch (error) {
  console.error("Validation failed:", error);
  // Model will retry or return error
}
```
