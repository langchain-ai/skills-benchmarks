---
name: LangGraph Streaming (Python)
description: "[LangGraph] Streaming real-time updates from LangGraph: stream modes (values, updates, messages, custom, debug) for responsive UX"
---

# langgraph-streaming (Python)


## Overview

LangGraph's streaming system surfaces real-time updates during graph execution, crucial for responsive LLM applications. Stream graph state, LLM tokens, or custom data as it's generated.

## Decision Table: Stream Modes

| Mode | What it Streams | Use Case |
|------|----------------|----------|
| `values` | Full state after each step | Monitor complete state changes |
| `updates` | State deltas after each step | Track incremental updates |
| `messages` | LLM tokens + metadata | Chat UIs, token streaming |
| `custom` | User-defined data | Progress indicators, logs |
| `debug` | All execution details | Debugging, detailed tracing |

## Code Examples

### Stream State Values

```python
from langgraph.graph import StateGraph, START, END

def process(state):
    return {"count": state["count"] + 1}

graph = StateGraph(State).add_node("process", process).add_edge(START, "process").add_edge("process", END).compile()

# Stream full state after each step
for chunk in graph.stream(
    {"count": 0},
    stream_mode="values"
):
    print(chunk)  # {'count': 0}, then {'count': 1}
```

### Stream State Updates (Deltas)

```python
# Stream only the changes
for chunk in graph.stream(
    {"count": 0},
    stream_mode="updates"
):
    print(chunk)  # {"process": {"count": 1}}
```

### Stream LLM Tokens

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

### Stream Custom Data

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

for chunk in graph.stream(
    {"data": "test"},
    stream_mode="custom"
):
    print(chunk)  # "Processing step 1...", etc.
```

### Multiple Stream Modes

```python
# Stream multiple modes simultaneously
for mode, chunk in graph.stream(
    {"messages": [HumanMessage("Hi")]},
    stream_mode=["updates", "messages", "custom"]
):
    print(f"{mode}: {chunk}")
```

### Async Streaming

```python
async for chunk in graph.astream(
    {"count": 0},
    stream_mode="values"
):
    print(chunk)
```

### Stream with Subgraphs

```python
# Include subgraph outputs
for chunk in graph.stream(
    {"data": "test"},
    stream_mode="updates",
    subgraphs=True  # Stream from nested graphs too
):
    print(chunk)
```

### Stream with Interrupts

```python
async for metadata, mode, chunk in graph.astream(
    {"query": "test"},
    stream_mode=["messages", "updates"],
    subgraphs=True,
    config={"configurable": {"thread_id": "1"}}
):
    if mode == "messages":
        # Handle streaming LLM content
        msg, _ = chunk
        if hasattr(msg, "content"):
            print(msg.content, end="")
    
    elif mode == "updates":
        # Check for interrupts
        if "__interrupt__" in chunk:
            # Handle interrupt
            interrupt_info = chunk["__interrupt__"][0].value
            user_input = input(f"Approve? {interrupt_info}: ")
            # Resume
            break
```

## Boundaries

### What You CAN Configure

✅ Choose stream modes
✅ Stream multiple modes simultaneously
✅ Emit custom data from nodes
✅ Stream from subgraphs
✅ Combine streaming with interrupts

### What You CANNOT Configure

❌ Modify streaming protocol
❌ Change when checkpoints are created
❌ Alter token streaming format

## Gotchas

### 1. Messages Mode Requires LLM Invocation

```python
# ❌ WRONG - No LLM called, nothing streamed
def node(state):
    return {"output": "static text"}

for chunk in graph.stream({}, stream_mode="messages"):
    print(chunk)  # Nothing!

# ✅ CORRECT - LLM invoked
def node(state):
    response = model.invoke(state["messages"])  # LLM call
    return {"messages": [response]}
```

### 2. Custom Mode Needs Stream Writer

```python
# ❌ WRONG - No writer, nothing streamed
def node(state):
    print("Processing...")  # Not streamed!
    return {"data": "done"}

# ✅ CORRECT
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer("Processing...")  # Streamed!
    return {"data": "done"}
```

### 3. Stream Modes Are Lists

```python
# ❌ WRONG - Single string
graph.stream({}, stream_mode="updates, messages")

# ✅ CORRECT - List
graph.stream({}, stream_mode=["updates", "messages"])
```

### 4. Async Stream Requires Await

```python
# ❌ WRONG
for chunk in graph.astream({}):  # SyntaxError!
    print(chunk)

# ✅ CORRECT
async for chunk in graph.astream({}):
    print(chunk)
```

## Links

- [Streaming Guide](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Stream Modes](https://docs.langchain.com/oss/python/langgraph/streaming#supported-stream-modes)
- [Custom Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
