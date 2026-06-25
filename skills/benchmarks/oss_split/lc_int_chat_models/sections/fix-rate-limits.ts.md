Configure retries for rate limit handling.

```typescript
// No retry logic
const model = new ChatOpenAI();
const response = await model.invoke("Hello"); // May fail on rate limit

// Configure retries
const model = new ChatOpenAI({
  maxRetries: 3,
  timeout: 30000, // 30 seconds
});
```
