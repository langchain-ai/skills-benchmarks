Define a classification schema with constrained enum values using z.enum().
```typescript
import { z } from "zod";

const Classification = z.object({
  category: z.enum(["urgent", "normal", "low"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  confidence: z.number().min(0).max(1),
});
```
