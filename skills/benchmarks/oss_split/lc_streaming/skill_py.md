---
name: LangChain Streaming (Python)
description: [LangChain] Stream outputs from LangChain agents and models - includes stream modes, token streaming, progress updates, and real-time feedback
---

<overview>
Streaming allows you to surface real-time updates from LangChain agents and models as they run. Instead of waiting for complete responses, you can display output progressively, improving user experience especially for long-running operations.

**Key Concepts:**
- **Stream Modes**: Different types of data streams (values, updates, messages, custom)
- **Token Streaming**: LLM tokens as they're generated
- **Agent Progress**: State updates after each agent step
- **Custom Updates**: User-defined progress signals
</overview>

<when-to-use-streaming>
| Scenario | Stream? | Why |
|----------|---------|-----|
| Long model responses | Yes | Show tokens as generated |
| Multi-step agent tasks | Yes | Show progress through steps |
| Long-running tools | Yes | Provide progress updates |
| Simple quick requests | Partial Maybe | Overhead might not be worth it |
| Backend batch processing | No | No user waiting for updates |
</when-to-use-streaming>

<stream-mode-selection>
| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples |
| `"custom"` | Need custom progress signals | User-defined data |
| Multiple modes | Need combined data | List of modes |
</stream-mode-selection>

<ex-basic-model-token-streaming>
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
# Output appears progressively: "Quantum" "computing" "is" ...
```
</ex-basic-model-token-streaming>

<ex-agent-progress-streaming>
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
</ex-agent-progress-streaming>

<ex-combined-streaming>
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
</ex-combined-streaming>

<ex-stream-with-values-mode>
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
</ex-stream-with-values-mode>

<ex-custom-progress-updates>
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
</ex-custom-progress-updates>

<ex-streaming-in-fastapi>
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
</ex-streaming-in-fastapi>

<ex-error-handling-in-streams>
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
</ex-error-handling-in-streams>

<ex-async-streaming>
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
</ex-async-streaming>

<ex-buffering-tokens>
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
</ex-buffering-tokens>

<ex-stream-with-context-manager>
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
</ex-stream-with-context-manager>

<boundaries>
### What You CAN Configure

* Stream modes**: Choose which data to stream
* Multiple modes**: Combine different stream types
* Custom updates**: Emit user-defined progress data
* Chunk processing**: Handle each chunk as needed
* Error handling**: Catch and handle stream errors

### What You CANNOT Configure

* Chunk size**: Determined by model/provider
* Chunk timing**: Arrives as provider sends
* Guarantee order**: Async streams may vary
* Modify past chunks**: Chunks are immutable
</boundaries>

<fix-tuple-unpacking-for-messages-mode>
```python
# WRONG: Problem: Not unpacking messages mode
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    print(chunk.content)  # AttributeError!

# CORRECT: Solution: Messages mode returns (token, metadata) tuple
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)  # Correct!
```
</fix-tuple-unpacking-for-messages-mode>

<fix-stream-mode-confusion>
```python
# WRONG: Problem: Using wrong mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk.content)  # AttributeError!

# CORRECT: Solution: Use "messages" mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)
```
</fix-stream-mode-confusion>

<fix-sync-vs-async>
```python
# WRONG: Problem: Using sync stream in async context
async def process():
    for mode, chunk in agent.stream(input):  # Blocks async loop!
        print(chunk)

# CORRECT: Solution: Use astream for async
async def process():
    async for mode, chunk in agent.astream(input):
        print(chunk)
```
</fix-sync-vs-async>

<fix-not-handling-all-modes>
```python
# WRONG: Problem: Not checking mode in multi-mode streaming
for mode, chunk in agent.stream(
    input,
    stream_mode=["updates", "messages"]
):
    print(chunk.content)  # Will fail for updates mode

# CORRECT: Solution: Check mode before accessing
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
</fix-not-handling-all-modes>

<fix-flush-for-realtime-display>
```python
# WRONG: Problem: Output not appearing in real-time
for chunk in model.stream("Long response"):
    print(chunk.content)  # May be buffered

# CORRECT: Solution: Use flush=True
for chunk in model.stream("Long response"):
    print(chunk.content, end="", flush=True)  # Real-time display
```
</fix-flush-for-realtime-display>

<fix-generator-exhaustion>
```python
# WRONG: Problem: Re-using exhausted generator
stream = agent.stream(input)
for mode, chunk in stream:
    print(chunk)

for mode, chunk in stream:  # Empty! Generator exhausted
    print(chunk)

# CORRECT: Solution: Create new stream each time
for mode, chunk in agent.stream(input):
    print(chunk)

# Later...
for mode, chunk in agent.stream(input):  # New stream
    print(chunk)
```
</fix-generator-exhaustion>

<links>
- [Streaming Overview](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- [LangGraph Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Model Streaming](https://docs.langchain.com/oss/python/langchain/models)
- [Human-in-the-Loop Streaming](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
</links>
