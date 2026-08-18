Optional fields and default values.

```typescript
import { z } from "zod";

const EventSchema = z.object({
  title: z.string(),
  date: z.string(),
  location: z.string().optional(),
  attendees: z.array(z.string()).default([]),
  confirmed: z.boolean().default(false),
});
```
