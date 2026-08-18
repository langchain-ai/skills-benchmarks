Get movie details as a validated Zod object using withStructuredOutput().
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const Movie = z.object({
  title: z.string().describe("Movie title"),
  year: z.number().describe("Release year"),
  director: z.string(),
  rating: z.number().min(0).max(10),
});

const model = new ChatOpenAI({ model: "gpt-4" });
const structuredModel = model.withStructuredOutput(Movie);

const response = await structuredModel.invoke("Tell me about Inception");
// { title: "Inception", year: 2010, director: "Christopher Nolan", rating: 8.8 }
```
