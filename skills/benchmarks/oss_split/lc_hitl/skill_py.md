---
name: langchain-human-in-the-loop-py
description: "[LangChain] Add human oversight to LangChain agents using HITL middleware - includes interrupts, approval workflows, edit/reject decisions, and checkpoints"
---

<overview>
Human-in-the-Loop (HITL) lets you add human oversight to agent tool calls. When agents propose sensitive actions (like database writes or sending emails), execution pauses for human approval, editing, or rejection.

**Key Concepts:**
- **HumanInTheLoopMiddleware**: Pauses execution for human decisions
- **Interrupts**: Checkpoint where agent waits for human input
- **Decisions**: approve, edit, or reject tool calls
- **Checkpointer**: Required for persistence across interruptions
</overview>

<ex-basic-hitl-setup>
```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    # Send email logic
    return f"Email sent to {to}"

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required for HITL
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
            }
        )
    ],
)
```
</ex-basic-hitl-setup>

<ex-running-with-interrupts>
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
result2 = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)

# Tool now executes and agent completes
print(result2["messages"][-1].content)
```
</ex-running-with-interrupts>

<ex-editing-tool-arguments>
```python
# Human edits the arguments — edited_action must include name + args
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {
                    "to": "alice@company.com",  # Fixed email
                    "subject": "Project Meeting - Updated",
                    "body": "...",
                },
            },
        }]
    }),
    config=config
)
```
</ex-editing-tool-arguments>

<ex-rejecting-with-feedback>
```python
# Human rejects
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "reject",
            "feedback": "Cannot delete customer data without manager approval",
        }]
    }),
    config=config
)
```
</ex-rejecting-with-feedback>

<ex-multiple-tools-different-policies>
```python
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email, read_email, delete_email],
    checkpointer=MemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "delete_email": {
                    "allowed_decisions": ["approve", "reject"],  # No edit
                },
                "read_email": False,  # No HITL for reading
            }
        )
    ],
)
```
</ex-multiple-tools-different-policies>

<ex-streaming-with-hitl>
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
</ex-streaming-with-hitl>

<fix-missing-checkpointer>
```python
# WRONG: Problem: No checkpointer
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    middleware=[HumanInTheLoopMiddleware({...})],  # Error!
)

# CORRECT: Solution: Always add checkpointer
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required
    middleware=[HumanInTheLoopMiddleware({...})],
)
```
</fix-missing-checkpointer>

<fix-no-thread-id>
```python
# WRONG: Problem: Missing thread_id
agent.invoke(input)  # No config!

# CORRECT: Solution: Always provide thread_id
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
</fix-no-thread-id>

<fix-wrong-resume-syntax>
```python
# WRONG: Problem: Wrong resume format
agent.invoke({"resume": {"decisions": [...]}})  # Wrong!

# CORRECT: Solution: Use Command
from langgraph.types import Command

agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
```
</fix-wrong-resume-syntax>

<links>
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
</links>
