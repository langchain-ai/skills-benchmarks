Use withStructuredOutput on model directly.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const MovieSchema = z.object({
  title: z.string().describe("Movie title"),
  year: z.number().describe("Release year"),
  director: z.string(),
  rating: z.number().min(0).max(10),
});

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(MovieSchema);

const response = await structuredModel.invoke("Tell me about Inception");
console.log(response);
// { title: "Inception", year: 2010, director: "Christopher Nolan", rating: 8.8 }
```
