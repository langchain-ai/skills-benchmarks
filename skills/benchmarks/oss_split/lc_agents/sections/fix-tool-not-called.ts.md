Vague vs clear tool descriptions:

```typescript
// Bad: Vague tool description
const badTool = tool(
  async ({ input }: { input: string }) => "result",
  {
    name: "tool",
    description: "Does stuff", // Too vague!
    schema: z.object({ input: z.string() }),
  }
);

// Good: Clear, specific descriptions
const goodTool = tool(
  async ({ query }: { query: string }) => "result",
  {
    name: "web_search",
    description: "Search the web for current information about a topic. Use this when you need recent data that wasn't in your training.",
    schema: z.object({
      query: z.string().describe("The search query (2-10 words)"),
    }),
  }
);
```
