Create agent with HITL middleware.

```typescript
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { z } from "zod";

const sendEmail = tool(
  async ({ to, subject, body }) => `Email sent to ${to}`,
  {
    name: "send_email",
    description: "Send an email",
    schema: z.object({ to: z.string().email(), subject: z.string(), body: z.string() }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required for HITL
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        send_email: { allowedDecisions: ["approve", "edit", "reject"] },
      },
    }),
  ],
});
```
