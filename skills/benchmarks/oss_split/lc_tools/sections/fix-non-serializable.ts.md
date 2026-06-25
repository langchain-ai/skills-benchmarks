TypeScript equivalent:

```typescript
// BAD: Returning complex objects
const badTool = tool(async () => new Date(), { name: "get_time", description: "Get time", schema: z.object({}) });

// GOOD: Return strings or JSON
const goodTool = tool(async () => new Date().toISOString(), { name: "get_time", description: "Get time", schema: z.object({}) });
```
