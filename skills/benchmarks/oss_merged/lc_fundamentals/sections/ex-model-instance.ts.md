Pass a model instance with custom settings instead of a model string.
```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({ model: "claude-sonnet-4-5", temperature: 0 });
const agent = createAgent({ model, tools: [...] });
```
