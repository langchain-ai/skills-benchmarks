---
name: Deep Agents Human-in-the-Loop (Python)
description: [Deep Agents] Implementing human-in-the-loop approval workflows with interrupt_on parameter for sensitive tool operations in Deep Agents.
---

# deepagents-hitl (Python)

## Overview

Human-in-the-Loop (HITL) middleware adds human oversight to tool calls. When the agent proposes a sensitive action, execution pauses for human decision:
- **approve**: Execute as-is
- **edit**: Modify before executing
- **reject**: Cancel with feedback

Requires LangGraph's persistence (checkpointer) to save state during interrupts.

## When to Use HITL

| Use HITL When | Skip HITL When |
|--------------|---------------|
| High-stakes operations (DB writes, deployments) | Read-only operations |
| Compliance requires human oversight | Fully automated workflows |
| Expensive API calls need verification | Low-cost operations |
| Learning agent behavior | Trusted, tested operations |

## Basic Setup

### Configure interrupts in create_deep_agent

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

## Decision Table: Interrupt Strategies

| Tool Type | Interrupt Config | Allowed Decisions | Use Case |
|-----------|-----------------|------------------|----------|
| Destructive | `True` | approve, edit, reject | write_file, delete_record |
| Critical | `{"allowed_decisions": ["approve", "reject"]}` | approve, reject only | deploy_code, execute_sql |
| Safe | `False` | none | read_file, get_weather |
| Expensive | `True` | approve, edit, reject | call_paid_api |

## Code Examples

### Example 1: Basic Approval Workflow

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

### Example 2: Approve Interrupt

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import Command

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

### Example 3: Edit Before Execution

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import Command

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
                        "args": {
                            "query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
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

### Example 4: Reject with Feedback

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import Command

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

### Example 5: Custom Interrupt Messages

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
                    "description": "🚨 PRODUCTION DEPLOYMENT requires approval"
                },
                "send_email": {
                    "description": "📧 Email draft ready for review"
                },
            },
        ),
    ],
    checkpointer=MemorySaver(),
)
```

## Boundaries

### What Agents CAN Configure

✅ Which tools require approval
✅ Allowed decision types per tool
✅ Custom interrupt descriptions
✅ Checkpointer implementation
✅ Interrupt handling logic

### What Agents CANNOT Configure

❌ The HITL protocol (approve/edit/reject structure)
❌ Skip checkpointer requirement
❌ Interrupt without saving state
❌ Have subagents interrupt without main checkpointer

## Gotchas

### 1. Checkpointer is REQUIRED

```python
# ❌ This will error
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# ✅ Must provide checkpointer
agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```

### 2. Thread ID Required for Resumption

```python
# ❌ Can't resume without thread_id
agent.invoke({"messages": [...]})
agent.update_state(...)  # Which thread?

# ✅ Use consistent thread_id
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
agent.update_state(config, ...)
```

### 3. Interrupt Checks Between Invocations

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

### 4. Edit Must Match Tool Schema

```python
# ❌ Edited args must match tool schema
agent.update_state(config, {
    "messages": [Command(resume={
        "decisions": [{
            "type": "edit",
            "args": {"wrong_param": "value"}  # Tool doesn't have this param
        }]
    })]
})

# ✅ Use correct parameter names from tool schema
```

## Full Documentation

- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [HITL Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
