Always describe schema fields:

```typescript
// BAD: No field descriptions
const badSchema = z.object({ query: z.string(), limit: z.number() });

// GOOD: Describe each field
const goodSchema = z.object({
  query: z.string().describe("Search terms or keywords"),
  limit: z.number().describe("Maximum results to return (1-100)"),
});
```
