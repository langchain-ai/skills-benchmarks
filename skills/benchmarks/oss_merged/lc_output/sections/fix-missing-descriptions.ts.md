Add field descriptions to guide the model on expected formats.
```typescript
// WRONG
const Data = z.object({ date: z.string(), amount: z.number() });

// CORRECT
const Data = z.object({
  date: z.string().describe("Date in YYYY-MM-DD format"),
  amount: z.number().describe("Amount in USD"),
});
```
