Use GPT-4 or similar for tool calling.

```typescript
// Model doesn't support tool calling
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This model doesn't support tools!

// Use tool-capable model
const model = new ChatOpenAI({ modelName: "gpt-4" });
const modelWithTools = model.bindTools([myTool]);
```
