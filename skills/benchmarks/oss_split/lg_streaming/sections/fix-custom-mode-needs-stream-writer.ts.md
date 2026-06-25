Use config.writer for custom data:

```typescript
// WRONG - No writer, nothing streamed
const node = async (state) => {
  console.log("Processing...");  // Not streamed!
  return { data: "done" };
};

// CORRECT
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const node = async (state, config: LangGraphRunnableConfig) => {
  config.writer?.("Processing...");  // Streamed!
  return { data: "done" };
};
```
