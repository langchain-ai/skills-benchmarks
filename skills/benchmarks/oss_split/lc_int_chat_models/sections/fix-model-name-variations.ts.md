Provider-specific model naming conventions.

```typescript
// Different providers have different model naming conventions
// OpenAI
const openai = new ChatOpenAI({ modelName: "gpt-4" });

// Bedrock (includes provider prefix)
const bedrock = new ChatBedrockConverse({
  model: "anthropic.claude-3-sonnet-20240229-v1:0"
});

// Anthropic (direct model name)
const anthropic = new ChatAnthropic({
  modelName: "claude-3-opus-20240229"
});
```
