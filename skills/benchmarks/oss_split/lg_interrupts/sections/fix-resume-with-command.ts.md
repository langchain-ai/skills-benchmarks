Use Command to resume:

```typescript
// WRONG - Passing regular object
await graph.invoke({ resumeData: "approve" }, config);  // Restarts!

// CORRECT - Use Command
import { Command } from "@langchain/langgraph";
await graph.invoke(new Command({ resume: "approve" }), config);
```
