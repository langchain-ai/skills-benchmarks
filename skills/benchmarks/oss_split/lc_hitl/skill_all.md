---
name: LangChain Human-in-the-Loop
description: "[LangChain] Add human oversight to LangChain agents using HITL middleware - includes interrupts, approval workflows, edit/reject decisions, and checkpoints"
---

<oneliner>
Human-in-the-Loop (HITL) lets you add human oversight to agent tool calls, pausing execution for approval, editing, or rejection of sensitive actions.
</oneliner>

<overview>
Key Concepts:
- **HumanInTheLoopMiddleware**: Pauses execution for human decisions
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

<decision-types>

| Decision | Effect | When to Use |
|----------|--------|-------------|
| `approve` | Execute tool as-is | Tool call looks correct |
| `edit` | Modify args then execute | Need to change parameters |
| `reject` | Don't execute, provide feedback | Tool call is wrong |

</decision-types>

<ex-setup>
<python>

Create agent with HITL middleware.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required for HITL
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
            }
        )
    ],
)
```

</python>

<typescript>

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

</typescript>
</ex-setup>

<ex-interrupts>
<python>

Invoke agent, check interrupt, then approve.

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent runs until it needs to call tool
result1 = agent.invoke({
    "messages": [{"role": "user", "content": "Send email to john@example.com saying hello"}]
}, config=config)

# Check for interrupt
if "__interrupt__" in result1:
    interrupt = result1["__interrupt__"][0]
    print(f"Waiting for approval: {interrupt.value}")

# Step 2: Human approves
result2 = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
print(result2["messages"][-1].content)
```

</python>

<typescript>

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

</typescript>
</ex-interrupts>

<ex-edit>
<python>

Edit tool arguments before execution.

```python
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {"to": "alice@company.com", "subject": "Updated", "body": "..."}
            },
        }]
    }),
    config=config
)
```

</python>

<typescript>

Edit tool arguments before execution.

```typescript
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{ type: "edit", editedAction: { name: "send_email", args: { to: "alice@company.com", subject: "Updated", body: "..." } } }],
    },
  }),
  config
);
```

</typescript>
</ex-edit>

<ex-reject>
<python>

Reject tool call with feedback.

```python
result2 = agent.invoke(
    Command(resume={
        "decisions": [{"type": "reject", "feedback": "Cannot delete without manager approval"}]
    }),
    config=config
)
```

</python>

<typescript>

Reject tool call with feedback.

```typescript
const result2 = await agent.invoke(
  new Command({
    resume: { decisions: [{ type: "reject", feedback: "Cannot delete without manager approval" }] },
  }),
  config
);
```

</typescript>
</ex-reject>

<ex-policies>
<python>

Per-tool HITL policy configuration.

```python
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email, read_email, delete_email],
    checkpointer=MemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "delete_email": {"allowed_decisions": ["approve", "reject"]},  # No edit
                "read_email": False,  # No HITL for reading
            }
        )
    ],
)
```

</python>

<typescript>

Per-tool HITL policy configuration.

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail, readEmail, deleteEmail],
  checkpointer: new MemorySaver(),
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        send_email: { allowedDecisions: ["approve", "edit", "reject"] },
        delete_email: { allowedDecisions: ["approve", "reject"] },  // No edit
        read_email: false,  // No HITL for reading
      },
    }),
  ],
});
```

</typescript>
</ex-policies>

<ex-streaming>
<python>

Stream responses with interrupt handling.

```python
# Stream until interrupt
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Send report to team"}]},
    config=config,
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        if "__interrupt__" in chunk:
            print("\nWaiting for approval...")
            break

# Resume after approval
for mode, chunk in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode=["messages"],
):
    # Continue streaming
    pass
```

</python>

<typescript>

Stream responses with interrupt handling.

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

</typescript>
</ex-streaming>

<ex-custom-logic>
<typescript>

Custom middleware with conditional interrupts.

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
</typescript>
</ex-custom-logic>

<boundaries>
What You CAN Configure:
- **Which tools require approval**: Per-tool policies
- **Allowed decision types**: approve, edit, reject
- **Custom interrupt logic**: Conditional interrupts
- **Feedback messages**: Explain rejections
- **Modified arguments**: Edit tool parameters

What You CANNOT Configure:
- **Skip checkpointer**: HITL requires persistence
- **Interrupt after execution**: Must interrupt before
- **Force model to not call tool**: HITL responds after model decides
- **Modify model's decision-making**: Only tool execution
</boundaries>

<fix-missing-checkpointer>
<python>
HITL requires a checkpointer - always add `MemorySaver()` or another persistence backend.

Add checkpointer to enable HITL.

```python
# Problem: No checkpointer
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    middleware=[HumanInTheLoopMiddleware({...})],  # Error!
)

# Solution: Always add checkpointer
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required
    middleware=[HumanInTheLoopMiddleware({...})],
)
```
</python>
<typescript>
HITL requires a checkpointer - always add `MemorySaver()` or another persistence backend.

Add checkpointer to enable HITL.

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
</typescript>
</fix-missing-checkpointer>

<fix-no-thread-id>
<python>
Always provide `thread_id` in config. Without it, the agent can't track state across invoke calls.

Include thread_id in config.

```python
# Problem: Missing thread_id
agent.invoke(input)  # No config!

# Solution: Always provide thread_id
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
</python>
<typescript>
Always provide `thread_id` in config. Without it, the agent can't track state across invoke calls.

Include thread_id in config.

```typescript
// Problem: Missing thread_id
await agent.invoke(input);  // No config!

// Solution: Always provide thread_id
await agent.invoke(input, {
  configurable: { thread_id: "user-123" }
});
```
</typescript>
</fix-no-thread-id>

<fix-wrong-resume-syntax>
<python>
Use `Command(resume={...})` (Python) or `new Command({ resume: {...} })` (TypeScript), not a plain dict/object.

Use Command class to resume.

```python
# Problem: Wrong resume format
agent.invoke({"resume": {"decisions": [...]}})  # Wrong!

# Solution: Use Command
from langgraph.types import Command

agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
```
</python>
<typescript>
Use `Command(resume={...})` (Python) or `new Command({ resume: {...} })` (TypeScript), not a plain dict/object.

Use Command class to resume.

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
</typescript>
</fix-wrong-resume-syntax>

<fix-not-checking-interrupts>
<python>
Check for `"__interrupt__"` in the result before assuming the agent completed.

Check for interrupt before processing result.

```python
# Problem: Not detecting interrupt
result = agent.invoke(input, config=config)
print(result["messages"])  # May not have completed!

# Solution: Check for __interrupt__
if "__interrupt__" in result:
    # Handle human decision
    pass
else:
    # Agent completed
    pass
```
</python>
<typescript>
Check for `"__interrupt__"` in the result before assuming the agent completed.

Check for interrupt before processing result.

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
</typescript>
</fix-not-checking-interrupts>

<links>
- Python: [Human-in-the-Loop Guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) | [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- TypeScript: [Human-in-the-Loop Guide](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop) | [Interrupts](https://docs.langchain.com/oss/javascript/langgraph/interrupts)
</links>
