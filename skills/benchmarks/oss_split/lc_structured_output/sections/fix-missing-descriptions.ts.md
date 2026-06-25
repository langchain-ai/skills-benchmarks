Add describe() calls for clarity.

```typescript
// Problem: No field descriptions
const schema = z.object({
  date: z.string(),  // What format?
  amount: z.number(),  // What unit?
});

// Solution: Add descriptions
const schema = z.object({
  date: z.string().describe("Date in YYYY-MM-DD format"),
  amount: z.number().describe("Amount in USD"),
});
```
