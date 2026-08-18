Get both raw message and parsed output.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const schema = z.object({ name: z.string(), age: z.number() });

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(schema, {
  includeRaw: true,
});

const response = await structuredModel.invoke("Person: Alice, 30 years old");
console.log(response);
// {
//   raw: AIMessage { ... },
//   parsed: { name: "Alice", age: 30 }
// }
```
