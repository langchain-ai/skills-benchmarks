Always wrap invoke in try/catch.

```typescript
// Problem: No error handling
const result = await agent.invoke(input);
const data = result.structuredResponse;  // May throw!

// Solution: Try/catch or check for errors
try {
  const result = await agent.invoke(input);
  const data = result.structuredResponse;
} catch (error) {
  console.error("Failed to get structured output:", error);
}
```
