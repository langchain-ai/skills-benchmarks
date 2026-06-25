Provide API key via environment variable.

```typescript
// Missing API key
const tool = new TavilySearchResults();
await tool.invoke("query"); // Error!

// Provide API key
const tool = new TavilySearchResults({
  apiKey: process.env.TAVILY_API_KEY,
});
```
