Create minimal agent with defaults:

```typescript
import { createDeepAgent } from "deepagents";

// Minimal agent with default settings
const agent = await createDeepAgent({});

// Invoke the agent
const result = await agent.invoke({
  messages: [
    { role: "user", content: "What's the weather in Tokyo?" }
  ]
});
```
