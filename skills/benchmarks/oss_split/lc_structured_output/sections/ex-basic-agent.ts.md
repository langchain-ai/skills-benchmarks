Extract contact info with Zod validation.

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string(),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactInfo,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract: John Doe, john@example.com, (555) 123-4567"
  }],
});

console.log(result.structuredResponse);
// { name: 'John Doe', email: 'john@example.com', phone: '(555) 123-4567' }
```
