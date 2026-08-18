Add custom descriptions per tool:

```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [deployTool, sendEmailTool],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        deploy_to_prod: {
          allowedDecisions: ["approve", "reject"],
          description: "PRODUCTION DEPLOYMENT requires approval"
        },
        send_email: {
          description: "Email draft ready for review"
        },
      },
    }),
  ],
  checkpointer: new MemorySaver(),
});
```
