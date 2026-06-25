Set API key for default model:

```typescript
// Uses claude-sonnet-4-5-20250929 by default
const agent = await createDeepAgent({});

// Requires ANTHROPIC_API_KEY environment variable
// Set OPENAI_API_KEY if using OpenAI models
process.env.ANTHROPIC_API_KEY = "your-key";
```
