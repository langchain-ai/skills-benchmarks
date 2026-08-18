Handle context length limits:

```typescript
// Problem: Input + output exceeds model limit
const longText = "...50,000 words...";
const model = await initChatModel("gpt-4.1"); // 128k context
await model.invoke(longText); // May succeed

const model2 = await initChatModel("gpt-4.1-mini"); // 16k context
await model2.invoke(longText); // Error: context too long

// Solution: Check input length or use larger context model
import { encoding_for_model } from "tiktoken";

const enc = encoding_for_model("gpt-4.1");
const tokens = enc.encode(longText);
console.log(`Input tokens: ${tokens.length}`);

if (tokens.length > 100000) {
  // Use Claude with 200k context
  const model = await initChatModel("anthropic:claude-opus-4");
}
```
