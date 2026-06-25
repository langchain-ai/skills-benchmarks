Always await async operations:

```typescript
// BAD: Not awaiting async operations
const badTool = tool(
  ({ url }) => { fetch(url); return "done"; },  // Not awaited!
  { name: "fetch_url", description: "Fetch URL", schema: z.object({ url: z.string() }) }
);

// GOOD: Use async/await
const goodTool = tool(
  async ({ url }) => {
    const response = await fetch(url);
    return await response.text();
  },
  { name: "fetch_url", description: "Fetch URL content", schema: z.object({ url: z.string().url() }) }
);
```
