Define nested Zod schemas for complex data.

```typescript
import { z } from "zod";

const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string(),
  zip: z.string(),
});

const PersonSchema = z.object({
  name: z.string(),
  age: z.number().int().positive(),
  email: z.string().email(),
  address: AddressSchema,
  tags: z.array(z.string()),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: PersonSchema,
});
```
