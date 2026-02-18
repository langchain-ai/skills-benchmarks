---
name: Deep Agents Human-in-the-Loop (TypeScript)
description: [Deep Agents] Implementing human-in-the-loop approval workflows with interrupt_on parameter for sensitive tool operations in Deep Agents.
---

# deepagents-hitl (JavaScript/TypeScript)

## Overview

HITL middleware adds human oversight to tool calls. Execution pauses for human decision: **approve**, **edit**, or **reject**.

Requires checkpointer to save state during interrupts.

## Basic Setup

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

## Decision Table

| Tool Type | Config | Decisions | Use Case |
|-----------|--------|-----------|----------|
| Destructive | `true` | approve/edit/reject | write_file, delete |
| Critical | `{allowedDecisions: [...]}` | approve/reject only | deploy, SQL |
| Safe | `false` | none | read_file |

## Code Examples

### Example 1: Basic Approval

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

### Example 2: Edit Before Execution

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
          args: {
            query: "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
          }
        }]
      }
    })
  ]
});

// Continue
await agent.invoke(null, config);
```

### Example 3: Reject with Feedback

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

### Example 4: Custom Middleware

```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4",
  tools: [deployTool, sendEmailTool],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        deploy_to_prod: {
          allowedDecisions: ["approve", "reject"],
          description: "🚨 PRODUCTION DEPLOYMENT requires approval"
        },
        send_email: {
          description: "📧 Email draft ready for review"
        },
      },
    }),
  ],
  checkpointer: new MemorySaver(),
});
```

## Boundaries

### What Agents CAN Configure
✅ Which tools require approval  
✅ Allowed decision types per tool  
✅ Custom interrupt descriptions  
✅ Checkpointer implementation

### What Agents CANNOT Configure
❌ HITL protocol structure  
❌ Skip checkpointer requirement  
❌ Interrupt without saving state

## Gotchas

### 1. Checkpointer is REQUIRED
```typescript
// ❌ Error
await createDeepAgent({ interruptOn: { write_file: true } });

// ✅ Must provide checkpointer
await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```

### 2. Thread ID Required
```typescript
// ❌ Can't resume without thread_id
await agent.invoke({...});
await agent.updateState(...);  // Which thread?

// ✅ Use consistent thread_id
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({...}, config);
await agent.updateState(config, ...);
```

### 3. Check State Between Invocations
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

## Full Documentation
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/javascript/deepagents/human-in-the-loop)
