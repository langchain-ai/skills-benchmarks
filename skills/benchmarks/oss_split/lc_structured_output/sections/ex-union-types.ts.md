Union types for multiple possible schemas.

```typescript
import { z } from "zod";

const EmailSchema = z.object({
  type: z.literal("email"),
  to: z.string().email(),
  subject: z.string(),
});

const PhoneSchema = z.object({
  type: z.literal("phone"),
  number: z.string(),
  message: z.string(),
});

const ContactSchema = z.union([EmailSchema, PhoneSchema]);

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactSchema,
});
// Model chooses which schema based on input
```
