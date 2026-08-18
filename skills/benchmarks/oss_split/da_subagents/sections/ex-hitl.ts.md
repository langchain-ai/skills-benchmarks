Require approval for deployment subagent:

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  subagents: [
    {
      name: "code-deployer",
      description: "Deploy code to production",
      systemPrompt: "Deploy code safely with all checks",
      tools: [runTests, deployToProd],
      interruptOn: { deploy_to_prod: true },  // Require approval
    }
  ],
  checkpointer: new MemorySaver()  // Required
});
```
