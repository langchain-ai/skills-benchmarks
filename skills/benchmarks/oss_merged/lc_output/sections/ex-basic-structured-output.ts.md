Extract contact information from text using a Zod schema with email validation.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string(),
});

const model = new ChatOpenAI({ model: "gpt-4" });
const structuredModel = model.withStructuredOutput(ContactInfo);

const response = await structuredModel.invoke(
  "Extract: John Doe, john@example.com, (555) 123-4567"
);
console.log(response);
// { name: 'John Doe', email: 'john@example.com', phone: '(555) 123-4567' }
```
