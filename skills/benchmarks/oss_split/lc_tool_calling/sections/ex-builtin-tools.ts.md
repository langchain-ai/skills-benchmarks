Use provider built-in tools.

```typescript
import { ChatOpenAI } from "@langchain/openai";

// OpenAI has built-in tools
const model = new ChatOpenAI({
  model: "gpt-4.1",
  // Enable code interpreter
  tools: [{ type: "code_interpreter" }],
});

// Anthropic has built-in tools
import { ChatAnthropic } from "@langchain/anthropic";

const claude = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  // These are provider parameters, not bindTools()
});
```
