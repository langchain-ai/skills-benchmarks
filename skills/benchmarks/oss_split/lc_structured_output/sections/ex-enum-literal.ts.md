Classify with z.enum for restricted values.

```typescript
import { z } from "zod";

const ClassificationSchema = z.object({
  category: z.enum(["urgent", "normal", "low"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  confidence: z.number().min(0).max(1),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ClassificationSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Classify: This is extremely important and I'm very happy!"
  }],
});
// { category: "urgent", sentiment: "positive", confidence: 0.95 }
```
