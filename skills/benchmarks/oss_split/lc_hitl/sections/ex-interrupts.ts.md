Invoke agent, check interrupt, then approve.

```typescript
import { Command } from "@langchain/langgraph";

const config = { configurable: { thread_id: "session-1" } };

// Step 1: Agent runs until it needs to call tool
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "Send email to john@example.com saying hello" }]
}, config);

// Check for interrupt
if ("__interrupt__" in result1) {
  console.log("Waiting for approval:", result1.__interrupt__[0].value);
}

// Step 2: Human approves
const result2 = await agent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  config
);
console.log(result2.messages[result2.messages.length - 1].content);
```
