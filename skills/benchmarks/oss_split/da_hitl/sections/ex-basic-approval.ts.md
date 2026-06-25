Invoke and check for interrupts:

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";
import { Command } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

// Step 1: Invoke (triggers interrupt)
let result = await agent.invoke({
  messages: [{ role: "user", content: "Write config to /prod.yaml" }]
}, config);

// Step 2: Check for interrupts
const state = await agent.getState(config);
if (state.next) {
  const interrupt = state.tasks[0];
  console.log("Interrupt:", interrupt);
}

// Step 3: Approve
await agent.updateState(config, {
  messages: [
    new Command({
      resume: {
        decisions: [{ type: "approve" }]
      }
    })
  ]
});

// Step 4: Continue
result = await agent.invoke(null, config);
```
