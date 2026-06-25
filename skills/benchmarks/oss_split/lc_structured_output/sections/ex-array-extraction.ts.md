Extract lists of items from text.

```typescript
import { z } from "zod";

const TaskListSchema = z.object({
  tasks: z.array(z.object({
    title: z.string(),
    priority: z.enum(["high", "medium", "low"]),
    dueDate: z.string().optional(),
  })),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: TaskListSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract tasks: 1. Fix bug (high priority, due tomorrow) 2. Update docs"
  }],
});
```
