Access structuredResponse, not response.

```typescript
// Problem: Accessing wrong property
const result = await agent.invoke(input);
console.log(result.response);  // undefined!

// Solution: Use structuredResponse
console.log(result.structuredResponse);
```
