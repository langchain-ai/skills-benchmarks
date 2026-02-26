---
name: LangGraph Execution Control (Python)
description: "INVOKE THIS SKILL for LangGraph workflows, parallel execution, interrupts, or streaming. Covers Send API for fan-out, interrupt() for human-in-the-loop, Command for resuming, and stream modes (values/updates/messages). CRITICAL: Fixes for interrupt without checkpointer, missing reducers for Send, and stream mode tuple unpacking."
---

<overview>
LangGraph provides execution control patterns for complex agent orchestration:

1. **Workflows vs Agents**: Predetermined paths vs dynamic decision-making
2. **Send API**: Fan-out to parallel workers (map-reduce)
3. **Interrupts**: Pause for human input, resume with Command
4. **Streaming**: Real-time state, tokens, and custom data
</overview>

<workflow-vs-agent>

| Characteristic | Workflow | Agent | Hybrid |
|----------------|----------|-------|--------|
| **Control Flow** | Fixed, predetermined | Dynamic, model-driven | Mixed |
| **Predictability** | High | Low | Medium |
| **Use Case** | Sequential tasks | Open-ended problems | Structured flexibility |

</workflow-vs-agent>

---

## Workflows and Agents

<ex-dynamic-agent>
```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

model = init_chat_model("claude-sonnet-4-5-20250929")
model_with_tools = model.bind_tools([search])

def agent_node(state: AgentState) -> dict:
    """Agent decides which tool to use (if any)."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute tools chosen by agent."""
    tools_by_name = {"search": search}
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

def should_continue(state: AgentState):
    """Dynamic: agent decides if it needs more tools."""
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# Dynamic agent: model decides when to stop
agent = (
    StateGraph(AgentState)
    .add_node("agent", agent_node)
    .add_node("tools", tool_node)
    .add_edge(START, "agent")
    .add_conditional_edges("agent", should_continue)  # Model decides
    .add_edge("tools", "agent")
    .compile()
)
```
</ex-dynamic-agent>

<ex-orchestrator-worker>
```python
from langgraph.types import Send
from typing import Annotated
import operator

class OrchestratorState(TypedDict):
    tasks: list[str]
    results: Annotated[list, operator.add]

def orchestrator(state: OrchestratorState):
    """Fan out tasks to workers."""
    return [
        Send("worker", {"task": task})
        for task in state["tasks"]
    ]

def worker(state: dict) -> dict:
    """Individual worker processes one task."""
    task = state["task"]
    result = f"Completed: {task}"
    return {"results": [result]}

def synthesize(state: OrchestratorState) -> dict:
    """Combine worker outputs."""
    summary = f"Processed {len(state['results'])} tasks"
    return {"summary": summary}

graph = (
    StateGraph(OrchestratorState)
    .add_node("worker", worker)
    .add_node("synthesize", synthesize)
    .add_conditional_edges(START, orchestrator, ["worker"])
    .add_edge("worker", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)

result = graph.invoke({"tasks": ["Task A", "Task B", "Task C"]})
```
</ex-orchestrator-worker>

---

## Interrupts (Human-in-the-Loop)

<interrupt-type-selection>

| Type | When Set | Use Case |
|------|----------|----------|
| Dynamic (`interrupt()`) | Inside node code | Conditional pausing based on logic |
| Static (`interrupt_before`) | At compile time | Debug/test before specific nodes |
| Static (`interrupt_after`) | At compile time | Review output after specific nodes |

</interrupt-type-selection>

<ex-dynamic-interrupt>
```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

def review_node(state):
    # Conditionally pause for review
    if state["needs_review"]:
        user_response = interrupt({
            "action": "review",
            "data": state["draft"],
            "question": "Approve this draft?"
        })

        # user_response comes from Command(resume=...)
        if user_response == "reject":
            return {"status": "rejected"}

    return {"status": "approved"}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("review", review_node)
    .add_edge(START, "review")
    .add_edge("review", END)
    .compile(checkpointer=checkpointer)  # Required!
)

# Initial invocation - will pause
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"needs_review": True, "draft": "content"}, config)

# Check for interrupt
if "__interrupt__" in result:
    print(result["__interrupt__"])  # See interrupt payload

# Resume with user decision
result = graph.invoke(
    Command(resume="approve"),  # User's response
    config
)
```
</ex-dynamic-interrupt>

<ex-static-breakpoints>
```python
checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_node("step3", step3)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", "step3")
    .add_edge("step3", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"],  # Pause before step2
        interrupt_after=["step3"]    # Pause after step3
    )
)

config = {"configurable": {"thread_id": "1"}}

# Run until first breakpoint
graph.invoke({"data": "test"}, config)

# Resume (pauses at next breakpoint)
graph.invoke(None, config)  # None = resume
```
</ex-static-breakpoints>

---

## Streaming

<stream-mode-selection>

| Mode | What it Streams | Use Case |
|------|----------------|----------|
| `values` | Full state after each step | Monitor complete state changes |
| `updates` | State deltas after each step | Track incremental updates |
| `messages` | LLM tokens + metadata | Chat UIs, token streaming |
| `custom` | User-defined data | Progress indicators, logs |

</stream-mode-selection>

<ex-stream-llm-tokens>
```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4")

def llm_node(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(State).add_node("llm", llm_node).compile()

# Stream LLM tokens as they're generated
for chunk in graph.stream(
    {"messages": [HumanMessage("Hello")]},
    stream_mode="messages"
):
    token, metadata = chunk
    if hasattr(token, "content"):
        print(token.content, end="", flush=True)
```
</ex-stream-llm-tokens>

<ex-stream-custom-data>
```python
from langgraph.config import get_stream_writer

def my_node(state):
    writer = get_stream_writer()

    # Emit custom updates
    writer("Processing step 1...")
    # Do work
    writer("Processing step 2...")
    # More work
    writer("Complete!")

    return {"result": "done"}

graph = StateGraph(State).add_node("work", my_node).compile()

for chunk in graph.stream({"data": "test"}, stream_mode="custom"):
    print(chunk)  # "Processing step 1...", etc.
```
</ex-stream-custom-data>

<ex-multiple-stream-modes>
```python
# Stream multiple modes simultaneously
for mode, chunk in graph.stream(
    {"messages": [HumanMessage("Hi")]},
    stream_mode=["updates", "messages", "custom"]
):
    print(f"{mode}: {chunk}")
```
</ex-multiple-stream-modes>

<boundaries>
### What You CAN Configure

- Choose workflow vs agent pattern
- Use Send API for parallel execution
- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)`
- Choose stream modes, stream multiple simultaneously
- Emit custom data from nodes

### What You CANNOT Configure

- Interrupt without checkpointer
- Resume without thread_id
- Change Send API message-passing model
- Modify streaming protocol
</boundaries>

<fix-send-accumulator>
```python
# WRONG: Last worker overwrites all others
class State(TypedDict):
    results: list  # No reducer!

# CORRECT: Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates
```
</fix-send-accumulator>

<fix-agent-guardrails>
```python
# RISKY: Pure agent, no guardrails - might loop forever
def should_continue(state):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# BETTER: Hybrid with constraints
def should_continue(state):
    # Add max iterations check
    if state["iterations"] > 10:
        return END
    if state["messages"][-1].tool_calls:
        return "tools"
    return END
```
</fix-agent-guardrails>

<fix-checkpointer-required-for-interrupts>
```python
# WRONG: No checkpointer - interrupt won't work
graph = builder.compile()
graph.invoke(...)  # Interrupt fails!

# CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
</fix-checkpointer-required-for-interrupts>

<fix-resume-with-command>
```python
# WRONG: Passing regular dict restarts graph
graph.invoke({"resume_data": "approve"}, config)

# CORRECT: Use Command to resume
from langgraph.types import Command
graph.invoke(Command(resume="approve"), config)
```
</fix-resume-with-command>

<fix-messages-mode-requires-llm>
```python
# WRONG: No LLM called, nothing streamed
def node(state):
    return {"output": "static text"}

for chunk in graph.stream({}, stream_mode="messages"):
    print(chunk)  # Nothing!

# CORRECT: LLM invoked
def node(state):
    response = model.invoke(state["messages"])  # LLM call
    return {"messages": [response]}
```
</fix-messages-mode-requires-llm>

<fix-custom-mode-needs-stream-writer>
```python
# WRONG: No writer, nothing streamed
def node(state):
    print("Processing...")  # Not streamed!
    return {"data": "done"}

# CORRECT
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer("Processing...")  # Streamed!
    return {"data": "done"}
```
</fix-custom-mode-needs-stream-writer>

<fix-stream-modes-are-lists>
```python
# WRONG: Single string
graph.stream({}, stream_mode="updates, messages")

# CORRECT: List
graph.stream({}, stream_mode=["updates", "messages"])
```
</fix-stream-modes-are-lists>
