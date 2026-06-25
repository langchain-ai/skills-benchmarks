Use clear, specific descriptions so model knows when to use the tool.
```typescript
// WRONG: Vague
const badTool = tool(async ({ data }) => "result", { name: "tool", description: "Does something", schema: z.object({ data: z.string() }) });

// CORRECT
const goodTool = tool(async ({ query }) => "result", {
  name: "web_search",
  description: "Search the web for current information",
  schema: z.object({ query: z.string().describe("Search query (2-10 words)") })
});
```
