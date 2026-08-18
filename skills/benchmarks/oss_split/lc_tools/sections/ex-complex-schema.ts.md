Nested Zod schema with optional fields:

```typescript
const searchDatabase = tool(
  async ({ query, limit, filters }) => {
    return `Found ${limit} results for: ${query}`;
  },
  {
    name: "search_database",
    description: "Search the customer database for records matching criteria",
    schema: z.object({
      query: z.string().describe("Search query (keywords or customer name)"),
      limit: z.number().default(10).describe("Maximum number of results to return"),
      filters: z.object({
        status: z.enum(["active", "inactive", "pending"]).optional(),
        created_after: z.string().optional().describe("ISO date string"),
      }).optional(),
    }),
  }
);
```
