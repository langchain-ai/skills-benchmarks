---
name: Deep Agents Human-in-the-Loop
description: "[Deep Agents] Implementing human-in-the-loop approval workflows with interrupt_on parameter for sensitive tool operations in Deep Agents."
---

<overview>
Human-in-the-Loop (HITL) middleware adds human oversight to tool calls. When the agent proposes a sensitive action, execution pauses for human decision:
- **approve**: Execute as-is
- **edit**: Modify before executing
- **reject**: Cancel with feedback

Requires LangGraph's persistence (checkpointer) to save state during interrupts.
</overview>

<when-to-use>

| Use HITL When | Skip HITL When |
|--------------|---------------|
| High-stakes operations (DB writes, deployments) | Read-only operations |
| Compliance requires human oversight | Fully automated workflows |
| Expensive API calls need verification | Low-cost operations |
| Learning agent behavior | Trusted, tested operations |

</when-to-use>

<setup>
<python>
### Configure interrupts in create_deep_agent

Configure which tools require approval:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={
        "write_file": True,  # All decisions allowed (approve/edit/reject)
        "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # No editing
        "read_file": False,  # No interrupts
    },
    checkpointer=MemorySaver()  # REQUIRED for interrupts
)
```

### Using HumanInTheLoopMiddleware Directly

Use middleware directly for custom agents:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4",
    tools=[write_file_tool, execute_sql_tool, read_data_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                "read_data": False,
            },
            description_prefix="Tool execution pending approval",
        ),
    ],
    checkpointer=MemorySaver(),
)
```
</python>

<typescript>
Configure which tools require approval:

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
</typescript>
</setup>

<decision-table>

| Tool Type | Interrupt Config | Allowed Decisions | Use Case |
|-----------|-----------------|------------------|----------|
| Destructive | `True` / `true` | approve, edit, reject | write_file, delete_record |
| Critical | `{"allowed_decisions": ["approve", "reject"]}` | approve, reject only | deploy_code, execute_sql |
| Safe | `False` / `false` | none | read_file, get_weather |
| Expensive | `True` / `true` | approve, edit, reject | call_paid_api |

</decision-table>

<ex-basic-approval>
<python>
Invoke and check for interrupts:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

# Initial invocation
config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "Write deployment config to /config/prod.yaml"}]
}, config=config)

# Execution pauses - check for interrupts
state = agent.get_state(config)
if state.next:  # Has interrupts
    for interrupt in state.tasks:
        print(f"Interrupt: {interrupt}")
```
</python>

<typescript>
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
</typescript>
</ex-basic-approval>

<ex-approve>
<python>
Approve a pending tool call:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent proposes write_file
result = agent.invoke({
    "messages": [{"role": "user", "content": "Write config to /prod.yaml"}]
}, config=config)

# Step 2: Get interrupts
state = agent.get_state(config)
interrupt = state.tasks[0]  # First interrupt

# Step 3: Approve
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{"type": "approve"}]
                }
            )
        ]
    }
)

# Step 4: Continue execution
result = agent.invoke(None, config=config)
```
</python>
</ex-approve>

<ex-edit>
<python>
Modify tool arguments before executing:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"execute_sql": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# Agent proposes SQL
result = agent.invoke({
    "messages": [{"role": "user", "content": "Delete old records from users table"}]
}, config=config)

# Get interrupt details
state = agent.get_state(config)
interrupt = state.tasks[0]
print(f"Proposed SQL: {interrupt.value['action_requests'][0]['args']}")

# Edit the SQL query
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "edit",
                        "edited_action": {
                            "name": "execute_sql",
                            "args": {
                                "query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
                            }
                        }
                    }]
                }
            )
        ]
    }
)

# Continue with edited query
result = agent.invoke(None, config=config)
```
</python>

<typescript>
Modify tool arguments before executing:

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
</typescript>
</ex-edit>

<ex-reject>
<python>
Reject and provide feedback to agent:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"deploy_code": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

result = agent.invoke({
    "messages": [{"role": "user", "content": "Deploy to production"}]
}, config=config)

# Reject deployment
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "reject",
                        "message": "Tests haven't passed yet. Run tests first."
                    }]
                }
            )
        ]
    }
)

# Agent receives rejection feedback and can try alternative approach
result = agent.invoke(None, config=config)
```
</python>

<typescript>
Reject and provide feedback to agent:

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
</typescript>
</ex-reject>

<ex-custom-messages>
<python>
Add custom descriptions per tool:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4",
    tools=[deploy_tool, send_email_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "deploy_to_prod": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "PRODUCTION DEPLOYMENT requires approval"
                },
                "send_email": {
                    "description": "Email draft ready for review"
                },
            },
        ),
    ],
    checkpointer=MemorySaver(),
)
```
</python>

<typescript>
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
</typescript>
</ex-custom-messages>

<boundaries>
**What Agents CAN Configure:**
- Which tools require approval
- Allowed decision types per tool
- Custom interrupt descriptions
- Checkpointer implementation
- Interrupt handling logic

**What Agents CANNOT Configure:**
- The HITL protocol (approve/edit/reject structure)
- Skip checkpointer requirement
- Interrupt without saving state
- Have subagents interrupt without main checkpointer
</boundaries>

<fix-checkpointer-required>
<python>
Provide checkpointer for interrupt state:

```python
# This will error
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# Must provide checkpointer
agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
</python>

<typescript>
Provide checkpointer for interrupt state:

```typescript
// Error
await createDeepAgent({ interruptOn: { write_file: true } });

// Must provide checkpointer
await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
</typescript>
</fix-checkpointer-required>

<fix-thread-id-required>
<python>
Use consistent thread_id to resume:

```python
# Can't resume without thread_id
agent.invoke({"messages": [...]})
agent.update_state(...)  # Which thread?

# Use consistent thread_id
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
agent.update_state(config, ...)
```
</python>

<typescript>
Use consistent thread_id to resume:

```typescript
// Can't resume without thread_id
await agent.invoke({...});
await agent.updateState(...);  // Which thread?

// Use consistent thread_id
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({...}, config);
await agent.updateState(config, ...);
```
</typescript>
</fix-thread-id-required>

<fix-interrupt-between-invocations>
<python>
Interrupts occur between invoke calls:

```python
# Interrupts don't happen mid-invoke()
# They happen between invoke() calls

# Step 1: invoke() -> interrupt occurs
result = agent.invoke({...}, config=config)

# Step 2: Check state for interrupts
state = agent.get_state(config)
if state.next:  # Has interrupts
    # Handle interrupts

# Step 3: Resume with decision
agent.update_state(config, {...})
result = agent.invoke(None, config=config)
```
</python>

<typescript>
Interrupts occur between invoke calls:

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
</typescript>
</fix-interrupt-between-invocations>

<fix-edit-match-tool-schema>
<python>
Use correct parameter names from schema:

```python
# Edited args must match tool schema
agent.update_state(config, {
    "messages": [Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {"name": "execute_sql", "args": {"wrong_param": "value"}}  # Tool doesn't have this param
        }]
    })]
})

# Use correct parameter names from tool schema
```
</python>
</fix-edit-match-tool-schema>

<links>
**Python:**
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)

**TypeScript:**
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/javascript/deepagents/human-in-the-loop)
</links>
