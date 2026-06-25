Set up an agent with HITL that pauses before sending emails for human approval.
```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const sendEmail = tool(
  async ({ to, subject, body }) => `Email sent to ${to}`,
  {
    name: "send_email",
    description: "Send an email",
    schema: z.object({ to: z.string(), subject: z.string(), body: z.string() }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required for HITL
  interruptBefore: ["send_email"],
});
```
