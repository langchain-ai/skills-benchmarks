TypeScript equivalent:

```typescript
// BAD: Vague description
const badTool = tool(
  async ({ data }) => "result",
  { name: "tool", description: "Does something with data", schema: z.object({ data: z.string() }) }
);

// GOOD: Specific, actionable description
const goodTool = tool(
  async ({ query }) => searchDatabase(query),
  {
    name: "search_customers",
    description: "Search customer database by name, email, or ID. Returns customer records with contact info.",
    schema: z.object({ query: z.string().describe("Customer name, email, or ID") }),
  }
);
```
