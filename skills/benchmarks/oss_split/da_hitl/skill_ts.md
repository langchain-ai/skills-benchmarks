---
name: deep-agents-human-in-the-loop-js
description: "[Deep Agents] Implementing human-in-the-loop approval workflows with interrupt_on parameter for sensitive tool operations in Deep Agents."
---

<overview>
HITL middleware adds human oversight to tool calls. Execution pauses for human decision: **approve**, **edit**, or **reject**.

Requires checkpointer to save state during interrupts.
</overview>

<basic-setup>
```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: {
    write_file: true,  // All decisions allowed
    execute_sql: { allowedDecisions: ["approve", "reject"] },  // No editing
    read_file: false,  // No interrupts
  },
  checkpointer: new MemorySaver()  // REQUIRED
});
```
</basic-setup>

<decision-table>

| Tool Type | Config | Decisions | Use Case |
|-----------|--------|-----------|----------|
| Destructive | `true` | approve/edit/reject | write_file, delete |
| Critical | `{allowedDecisions: [...]}` | approve/reject only | deploy, SQL |
| Safe | `false` | none | read_file |

</decision-table>

<ex-basic-approval>
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
</ex-basic-approval>

<ex-edit-before-execution>
```typescript
const agent = await createDeepAgent({
  interruptOn: { execute_sql: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

// Invoke
await agent.invoke({
  messages: [{ role: "user", content: "Delete old users" }]
}, config);

// Edit SQL
await agent.updateState(config, {
  messages: [
    new Command({
      resume: {
        decisions: [{
          type: "edit",
          editedAction: {
            name: "execute_sql",
            args: {
              query: "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
            }
          }
        }]
      }
    })
  ]
});

// Continue
await agent.invoke(null, config);
```
</ex-edit-before-execution>

<ex-reject-with-feedback>
```typescript
const agent = await createDeepAgent({
  interruptOn: { deploy_code: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

await agent.invoke({
  messages: [{ role: "user", content: "Deploy to production" }]
}, config);

// Reject
await agent.updateState(config, {
  messages: [
    new Command({
      resume: {
        decisions: [{
          type: "reject",
          message: "Tests haven't passed yet"
        }]
      }
    })
  ]
});

await agent.invoke(null, config);
```
</ex-reject-with-feedback>

<ex-custom-middleware>
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
</ex-custom-middleware>

<boundaries>
**What Agents CAN Configure**
- Which tools require approval
- Allowed decision types per tool
- Custom interrupt descriptions
- Checkpointer implementation

**What Agents CANNOT Configure**
- HITL protocol structure
- Skip checkpointer requirement
- Interrupt without saving state
</boundaries>

<fix-checkpointer-required>
```typescript
// WRONG: Error
await createDeepAgent({ interruptOn: { write_file: true } });

// CORRECT: Must provide checkpointer
await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
</fix-checkpointer-required>

<fix-thread-id-required>
```typescript
// WRONG: Can't resume without thread_id
await agent.invoke({...});
await agent.updateState(...);  // Which thread?

// CORRECT: Use consistent thread_id
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({...}, config);
await agent.updateState(config, ...);
```
</fix-thread-id-required>

<fix-check-state-between-invocations>
```typescript
// Interrupts happen between invoke() calls

// Step 1: invoke() -> interrupt
await agent.invoke({...}, config);

// Step 2: Check state
const state = await agent.getState(config);
if (state.next) {
  // Handle interrupts
}

// Step 3: Resume
await agent.updateState(config, {...});
await agent.invoke(null, config);
```
</fix-check-state-between-invocations>

<documentation-links>
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/javascript/deepagents/human-in-the-loop)
</documentation-links>
