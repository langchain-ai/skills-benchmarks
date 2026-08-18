Use environment variables for API keys.

```typescript
// BAD: Hardcoding API keys
const model = new ChatOpenAI({
  openAIApiKey: "sk-..."  // Never commit this!
});

// GOOD: Use environment variables
const model = new ChatOpenAI({
  openAIApiKey: process.env.OPENAI_API_KEY
});
```
