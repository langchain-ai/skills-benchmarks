Specify model by string or instance:

```typescript
import { createDeepAgent } from "deepagents";
import { ChatOpenAI } from "@langchain/openai";

// Use provider:model format
const agent = await createDeepAgent({
  model: "openai:gpt-4"
});

// Or pass a model instance
const model = new ChatOpenAI({ model: "gpt-4", temperature: 0 });
const agent2 = await createDeepAgent({
  model
});
```
