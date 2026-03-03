---
name: langchain-human-in-the-loop-js
description: "[LangChain] Add human oversight to LangChain agents using HITL middleware - includes interrupts, approval workflows, edit/reject decisions, and checkpoints"
---

<overview>
Human-in-the-Loop (HITL) lets you add human oversight to agent tool calls. When agents propose sensitive actions (like database writes or sending emails), execution pauses for human approval, editing, or rejection.

**Key Concepts:**
- **humanInTheLoopMiddleware**: Pauses execution for human decisions
- **Interrupts**: Checkpoint where agent waits for human input
- **Decisions**: approve, edit, or reject tool calls
- **Checkpointer**: Required for persistence across interruptions
</overview>

<when-to-use>

| Scenario | Use HITL? | Why |
|----------|-----------|-----|
| Database writes | Yes | Prevent data corruption |
| Sending emails/messages | Yes | Review before sending |
| Financial transactions | Yes | Confirm before executing |
| Deleting data | Yes | Prevent accidental loss |
| Read-only operations | No | Low risk |
| Internal calculations | No | No external impact |

</when-to-use>

<decision-types-table>

| Decision | Effect | When to Use |
|----------|--------|-------------|
| `approve` | Execute tool as-is | Tool call looks correct |
| `edit` | Modify args then execute | Need to change parameters |
| `reject` | Don't execute, provide feedback | Tool call is wrong |

</decision-types-table>

<ex-basic-setup>
```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { tool } from "langchain";
import { z } from "zod";

const sendEmail = tool(
  async ({ to, subject, body }) => {
    // Send email logic
    return `Email sent to ${to}`;
  },
  {
    name: "send_email",
    description: "Send an email",
    schema: z.object({
      to: z.string().email(),
      subject: z.string(),
      body: z.string(),
    }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required for HITL
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        send_email: {
          allowedDecisions: ["approve", "edit", "reject"],
        },
      },
    }),
  ],
});
```
</ex-basic-setup>

<ex-running-with-interrupts>
```typescript
import { Command } from "@langchain/langgraph";

const config = { configurable: { thread_id: "session-1" } };

// Step 1: Agent runs until it needs to call tool
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "Send email to john@example.com saying hello" }]
}, config);

// Check for interrupt
if ("__interrupt__" in result1) {
  const interrupt = result1.__interrupt__[0];
  console.log("Waiting for approval:", interrupt.value);

  // Interrupt contains: {toolCall: {...}, allowedDecisions: [...]}
}

// Step 2: Human approves
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{ type: "approve" }],
    },
  }),
  config
);

// Tool now executes and agent completes
console.log(result2.messages[result2.messages.length - 1].content);
```
</ex-running-with-interrupts>

<ex-editing-args>
```typescript
const config = { configurable: { thread_id: "session-2" } };

// Agent wants to send email
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "Email alice about the meeting" }]
}, config);

// Human edits the arguments
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{
        type: "edit",
        editedAction: {
          name: "send_email",
          args: {
            to: "alice@company.com",  // Fixed email
            subject: "Project Meeting - Updated",  // Better subject
            body: "...",  // Edited body
          },
        },
      }],
    },
  }),
  config
);
```
</ex-editing-args>

<ex-rejecting-with-feedback>
```typescript
const config = { configurable: { thread_id: "session-3" } };

// Agent wants to delete records
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "Delete old customer data" }]
}, config);

// Human rejects
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{
        type: "reject",
        feedback: "Cannot delete customer data without manager approval",
      }],
    },
  }),
  config
);

// Agent receives feedback and can try alternative approach
```
</ex-rejecting-with-feedback>

<ex-multiple-tools>
```typescript
import { humanInTheLoopMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail, readEmail, deleteEmail],
  checkpointer: new MemorySaver(),
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        send_email: {
          allowedDecisions: ["approve", "edit", "reject"],
        },
        delete_email: {
          allowedDecisions: ["approve", "reject"],  // No edit
        },
        read_email: false,  // No HITL for reading
      },
    }),
  ],
});
```
</ex-multiple-tools>

<ex-streaming-with-hitl>
```typescript
const config = { configurable: { thread_id: "session-4" } };

// Stream until interrupt
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Send report to team" }] },
  { ...config, streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    const [token, metadata] = chunk;
    if (token.content) {
      process.stdout.write(token.content);
    }
  } else if (mode === "updates") {
    if ("__interrupt__" in chunk) {
      console.log("\nWaiting for approval...");
      break;  // Handle interrupt
    }
  }
}

// Resume after approval
for await (const [mode, chunk] of await agent.stream(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  { ...config, streamMode: ["messages"] }
)) {
  // Continue streaming
}
```
</ex-streaming-with-hitl>

<ex-custom-logic>
```typescript
import { createMiddleware } from "langchain";

const customHITL = createMiddleware({
  name: "CustomHITL",
  wrapToolCall: async (toolCall, handler, runtime) => {
    // Custom logic to decide if interrupt needed
    if (toolCall.name === "database_write") {
      const value = toolCall.args.value;

      if (value > 1000) {
        // Interrupt for large values
        const decision = await runtime.interrupt({
          toolCall,
          reason: "Large database write requires approval",
        });

        if (decision.type === "approve") {
          return await handler(toolCall);
        } else if (decision.type === "edit") {
          return await handler({ ...toolCall, args: decision.args });
        } else {
          throw new Error(decision.feedback || "Rejected");
        }
      }
    }

    // No interrupt needed
    return await handler(toolCall);
  },
});
```
</ex-custom-logic>

<boundaries>
**What You CAN Configure**

* Which tools require approval**: Per-tool policies
* Allowed decision types**: approve, edit, reject
* Custom interrupt logic**: Conditional interrupts
* Feedback messages**: Explain rejections
* Modified arguments**: Edit tool parameters

**What You CANNOT Configure**

* Skip checkpointer**: HITL requires persistence
* Interrupt after execution**: Must interrupt before
* Force model to not call tool**: HITL responds after model decides
* Modify model's decision-making**: Only tool execution
</boundaries>

<fix-missing-checkpointer>
```typescript
// Problem: No checkpointer
const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  middleware: [humanInTheLoopMiddleware({...})],  // Error!
});

// Solution: Always add checkpointer
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required
  middleware: [humanInTheLoopMiddleware({...})],
});
```
</fix-missing-checkpointer>

<fix-no-thread-id>
```typescript
// Problem: Missing thread_id
await agent.invoke(input);  // No config!

// Solution: Always provide thread_id
await agent.invoke(input, {
  configurable: { thread_id: "user-123" }
});
```
</fix-no-thread-id>

<fix-wrong-resume-syntax>
```typescript
// Problem: Wrong resume format
await agent.invoke({
  resume: { decisions: [...] }  // Wrong!
});

// Solution: Use Command
import { Command } from "@langchain/langgraph";

await agent.invoke(
  new Command({
    resume: { decisions: [{ type: "approve" }] }
  }),
  config
);
```
</fix-wrong-resume-syntax>

<fix-not-checking-for-interrupts>
```typescript
// Problem: Not detecting interrupt
const result = await agent.invoke(input, config);
console.log(result.messages);  // May not have completed!

// Solution: Check for __interrupt__
if ("__interrupt__" in result) {
  // Handle human decision
} else {
  // Agent completed
}
```
</fix-not-checking-for-interrupts>

<documentation-links>
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in)
- [LangGraph Interrupts](https://docs.langchain.com/oss/javascript/langgraph/interrupts)
</documentation-links>
