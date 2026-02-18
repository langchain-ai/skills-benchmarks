---
name: LangChain Streaming (Python)
description: [LangChain] Stream outputs from LangChain agents and models - includes stream modes, token streaming, progress updates, and real-time feedback
---

# langchain-streaming (Python)

## Overview

Streaming allows you to surface real-time updates from LangChain agents and models as they run. Instead of waiting for complete responses, you can display output progressively, improving user experience especially for long-running operations.

**Key Concepts:**
- **Stream Modes**: Different types of data streams (values, updates, messages, custom)
- **Token Streaming**: LLM tokens as they're generated
- **Agent Progress**: State updates after each agent step
- **Custom Updates**: User-defined progress signals

## When to Use Streaming

| Scenario | Stream? | Why |
|----------|---------|-----|
| Long model responses | ✅ Yes | Show tokens as generated |
| Multi-step agent tasks | ✅ Yes | Show progress through steps |
| Long-running tools | ✅ Yes | Provide progress updates |
| Simple quick requests | ⚠️ Maybe | Overhead might not be worth it |
| Backend batch processing | ❌ No | No user waiting for updates |

## Decision Tables

### Stream Mode Selection

| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples |
| `"custom"` | Need custom progress signals | User-defined data |
| Multiple modes | Need combined data | List of modes |

## Code Examples

### Basic Model Token Streaming

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
# Output appears progressively: "Quantum" "computing" "is" ...
```

### Agent Progress Streaming

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool, calculator_tool],
)

# Stream agent steps with "updates" mode
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize"}]},
    stream_mode=["updates"],
):
    print(f"Step: {chunk}")
# Shows each step: model call, tool execution, final response
```

### Combined Streaming (Messages + Updates)

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

# Stream both LLM tokens AND agent progress
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research LangChain"}]},
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        # LLM token stream
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        # Agent step updates
        print(f"\nStep update: {chunk}")
```

### Stream with Values Mode

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[weather_tool],
)

# Get full state after each step
for mode, state in agent.stream(
    {"messages": [{"role": "user", "content": "What's the weather?"}]},
    stream_mode=["values"],
):
    print(f"Current messages: {len(state['messages'])}")
    print(f"Last message: {state['messages'][-1].content}")
```

### Custom Progress Updates from Tools

```python
from langchain.tools import tool

@tool
async def process_data(data: list, runtime) -> str:
    """Process data with progress updates."""
    total = len(data)
    
    for i in range(0, total, 100):
        # Emit custom progress update
        await runtime.stream_writer.write({
            "type": "progress",
            "data": {
                "processed": i,
                "total": total,
                "percentage": (i / total) * 100,
            },
        })
        
        # Do actual processing
        await process_chunk(data[i:i+100])
    
    return "Processing complete"

# Stream custom updates
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Process this data"}]},
    stream_mode=["custom", "updates"],
):
    if mode == "custom":
        print(f"Progress: {chunk['data']['percentage']}%")
```

### Streaming in FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
import json

app = FastAPI()

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

@app.post("/api/chat")
async def chat(messages: list):
    async def generate():
        try:
            async for mode, chunk in agent.astream(
                {"messages": messages},
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    token, metadata = chunk
                    if token.content:
                        # Send token to client
                        yield f"data: {json.dumps({'type': 'token', 'content': token.content})}\n\n"
                elif mode == "updates":
                    # Send step update to client
                    yield f"data: {json.dumps({'type': 'step', 'data': str(chunk)})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as error:
            yield f"data: {json.dumps({'type': 'error', 'message': str(error)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

### Error Handling in Streams

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[risky_tool],
)

try:
    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Do risky operation"}]},
        stream_mode=["updates"],
    ):
        # Check for errors in updates
        if "__error__" in chunk:
            print(f"Error in stream: {chunk['__error__']}")
            break
        
        print(f"Update: {chunk}")
except Exception as error:
    print(f"Stream error: {error}")
```

### Async Streaming

```python
from langchain.agents import create_agent
import asyncio

agent = create_agent(
    model="gpt-4.1",
    tools=[async_tool],
)

async def main():
    async for mode, chunk in agent.astream(
        {"messages": [{"role": "user", "content": "Process async"}]},
        stream_mode=["updates"],
    ):
        print(f"Update: {chunk}")

asyncio.run(main())
```

### Buffering Tokens for Display

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

buffer = ""
for chunk in model.stream("Write a long essay"):
    buffer += chunk.content
    
    # Update UI every 10 characters or on complete words
    if len(buffer) >= 10 or " " in chunk.content:
        print(buffer, end="", flush=True)
        buffer = ""

# Flush remaining buffer
if buffer:
    print(buffer, end="", flush=True)
```

### Stream with Context Manager

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

# Using context manager for cleanup
with agent.stream(
    {"messages": [{"role": "user", "content": "Search something"}]},
    stream_mode=["updates"],
) as stream:
    for mode, chunk in stream:
        print(chunk)
        if some_condition:
            break  # Properly cleaned up
```

## Boundaries

### What You CAN Configure

✅ **Stream modes**: Choose which data to stream
✅ **Multiple modes**: Combine different stream types
✅ **Custom updates**: Emit user-defined progress data
✅ **Chunk processing**: Handle each chunk as needed
✅ **Error handling**: Catch and handle stream errors

### What You CANNOT Configure

❌ **Chunk size**: Determined by model/provider
❌ **Chunk timing**: Arrives as provider sends
❌ **Guarantee order**: Async streams may vary
❌ **Modify past chunks**: Chunks are immutable

## Gotchas

### 1. Tuple Unpacking for Messages Mode

```python
# ❌ Problem: Not unpacking messages mode
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    print(chunk.content)  # AttributeError!

# ✅ Solution: Messages mode returns (token, metadata) tuple
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)  # Correct!
```

### 2. Stream Mode Confusion

```python
# ❌ Problem: Using wrong mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk.content)  # AttributeError!

# ✅ Solution: Use "messages" mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)
```

### 3. Sync vs Async

```python
# ❌ Problem: Using sync stream in async context
async def process():
    for mode, chunk in agent.stream(input):  # Blocks async loop!
        print(chunk)

# ✅ Solution: Use astream for async
async def process():
    async for mode, chunk in agent.astream(input):
        print(chunk)
```

### 4. Not Handling All Modes

```python
# ❌ Problem: Not checking mode in multi-mode streaming
for mode, chunk in agent.stream(
    input,
    stream_mode=["updates", "messages"]
):
    print(chunk.content)  # Will fail for updates mode

# ✅ Solution: Check mode before accessing
for mode, chunk in agent.stream(
    input,
    stream_mode=["updates", "messages"]
):
    if mode == "messages":
        token, metadata = chunk
        print(token.content)
    elif mode == "updates":
        print(f"Step: {chunk}")
```

### 5. Flush for Real-time Display

```python
# ❌ Problem: Output not appearing in real-time
for chunk in model.stream("Long response"):
    print(chunk.content)  # May be buffered

# ✅ Solution: Use flush=True
for chunk in model.stream("Long response"):
    print(chunk.content, end="", flush=True)  # Real-time display
```

### 6. Generator Exhaustion

```python
# ❌ Problem: Re-using exhausted generator
stream = agent.stream(input)
for mode, chunk in stream:
    print(chunk)

for mode, chunk in stream:  # Empty! Generator exhausted
    print(chunk)

# ✅ Solution: Create new stream each time
for mode, chunk in agent.stream(input):
    print(chunk)

# Later...
for mode, chunk in agent.stream(input):  # New stream
    print(chunk)
```

## Links to Documentation

- [Streaming Overview](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- [LangGraph Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Model Streaming](https://docs.langchain.com/oss/python/langchain/models)
- [Human-in-the-Loop Streaming](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
