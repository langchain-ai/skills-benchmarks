Define a tool with Zod schema for argument validation with default values.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchDatabase = tool(
  async ({ query, limit }) => `Found ${limit} results for: ${query}`,
  {
    name: "search_database",
    description: "Search the database for records",
    schema: z.object({
      query: z.string().describe("Search query"),
      limit: z.number().default(10).describe("Max results"),
    }),
  }
);
```
