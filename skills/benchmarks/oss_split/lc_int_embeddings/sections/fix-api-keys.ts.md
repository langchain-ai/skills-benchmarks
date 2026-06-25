Use environment variables for API keys.

```typescript
// Hardcoded API key
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: "sk-...", // Never commit this!
});

// Use environment variables
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// Even better: auto-detection
const embeddings = new OpenAIEmbeddings();
// Reads OPENAI_API_KEY from environment automatically
```
