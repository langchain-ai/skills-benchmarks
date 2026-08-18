Check provider-specific feature compatibility:

```typescript
// Problem: Using provider-specific feature with wrong model
const google = await initChatModel("google-genai:gemini-2.5-flash");
google.bindTools([tool]); // May not work the same way

// Solution: Check documentation for each provider
// OpenAI has specific tool calling format
// Anthropic has specific tool calling format
// Google has specific tool calling format

// Use initChatModel for portability, but be aware of differences
```
