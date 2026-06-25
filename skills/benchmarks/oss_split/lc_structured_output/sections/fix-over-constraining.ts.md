Avoid overly strict regex patterns.

```typescript
// Problem: Too strict for model
const schema = z.object({
  code: z.string().regex(/^[A-Z]{2}-\d{4}-[A-Z]{3}$/),  // Very specific!
});

// Solution: Validate post-processing or use looser schema
const schema = z.object({
  code: z.string().describe("Format: XX-0000-XXX (letters and numbers)"),
});
```
