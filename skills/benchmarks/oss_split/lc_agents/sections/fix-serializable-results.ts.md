Return JSON-serializable data from tools:

```typescript
// Problem: Returning non-serializable objects
const badTool = tool(
  async () => {
    return new Date(); // Date objects aren't JSON-serializable by default
  },
  { name: "get_time", description: "Get current time" }
);

// Solution: Return serializable data
const goodTool = tool(
  async () => {
    return new Date().toISOString(); // String is serializable
  },
  { name: "get_time", description: "Get current time" }
);
```
