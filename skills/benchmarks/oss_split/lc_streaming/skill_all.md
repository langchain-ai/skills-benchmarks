---
name: LangChain Streaming
description: "[LangChain] Stream outputs from LangChain agents and models - includes stream modes, token streaming, progress updates, and real-time feedback"
---

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
| Long model responses | Yes | Show tokens as generated |
| Multi-step agent tasks | Yes | Show progress through steps |
| Long-running tools | Yes | Provide progress updates |
| Simple quick requests | Maybe | Overhead might not be worth it |
| Backend batch processing | No | No user waiting for updates |

## Decision Tables

### Stream Mode Selection

| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict/object |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples / [token, metadata] arrays |
| `"custom"` | Need custom progress signals | User-defined data |
| Multiple modes | Need combined data | List/array of modes |

## Code Examples

### Basic Model Token Streaming

#### Python

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
# Output appears progressively: "Quantum" "computing" "is" ...
```

#### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

// Stream tokens as they arrive
const stream = await model.stream("Explain quantum computing in simple terms");

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
// Output appears progressively: "Quantum" "computing" "is" ...
```

### Agent Progress Streaming

#### Python

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

#### TypeScript

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
});

// Stream agent steps with "updates" mode
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for AI news and summarize" }] },
  { streamMode: "updates" }
)) {
  console.log("Step:", JSON.stringify(chunk, null, 2));
}
// Shows each step: model call, tool execution, final response
```

### Combined Streaming (Messages + Updates)

#### Python

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

#### TypeScript

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Stream both LLM tokens AND agent progress
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Research LangChain" }] },
  { streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    // LLM token stream
    const [token, metadata] = chunk;
    if (token.content) {
      process.stdout.write(token.content);
    }
  } else if (mode === "updates") {
    // Agent step updates
    console.log("\nStep update:", chunk);
  }
}
```

### Stream with Values Mode

#### Python

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

#### TypeScript

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [weatherTool],
});

// Get full state after each step
for await (const state of await agent.stream(
  { messages: [{ role: "user", content: "What's the weather?" }] },
  { streamMode: "values" }
)) {
  console.log("Current messages:", state.messages.length);
  console.log("Last message:", state.messages[state.messages.length - 1].content);
}
```

### Custom Progress Updates from Tools

#### Python

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

#### TypeScript

```typescript
import { tool } from "langchain";
import { z } from "zod";

const processData = tool(
  async ({ data }, { runtime }) => {
    const total = data.length;

    for (let i = 0; i < total; i += 100) {
      // Emit custom progress update
      await runtime.stream_writer.write({
        type: "progress",
        data: {
          processed: i,
          total: total,
          percentage: (i / total) * 100,
        },
      });

      // Do actual processing
      await processChunk(data.slice(i, i + 100));
    }

    return "Processing complete";
  },
  {
    name: "process_data",
    description: "Process data with progress updates",
    schema: z.object({
      data: z.array(z.any()),
    }),
  }
);

// Stream custom updates
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Process this data" }] },
  { streamMode: ["custom", "updates"] }
)) {
  if (mode === "custom") {
    console.log(`Progress: ${chunk.data.percentage}%`);
  }
}
```

### Streaming in Web Applications

#### Python (FastAPI)

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

#### TypeScript (Express.js)

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Express.js endpoint
app.post("/api/chat", async (req, res) => {
  // Set headers for Server-Sent Events
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  try {
    for await (const [mode, chunk] of await agent.stream(
      { messages: req.body.messages },
      { streamMode: ["messages", "updates"] }
    )) {
      if (mode === "messages") {
        const [token, metadata] = chunk;
        if (token.content) {
          // Send token to client
          res.write(`data: ${JSON.stringify({ type: "token", content: token.content })}\n\n`);
        }
      } else if (mode === "updates") {
        // Send step update to client
        res.write(`data: ${JSON.stringify({ type: "step", data: chunk })}\n\n`);
      }
    }

    res.write("data: [DONE]\n\n");
    res.end();
  } catch (error) {
    res.write(`data: ${JSON.stringify({ type: "error", message: error.message })}\n\n`);
    res.end();
  }
});
```

### Error Handling in Streams

#### Python

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

#### TypeScript

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [riskyTool],
});

try {
  for await (const chunk of await agent.stream(
    { messages: [{ role: "user", content: "Do risky operation" }] },
    { streamMode: "updates" }
  )) {
    // Check for errors in updates
    if ("__error__" in chunk) {
      console.error("Error in stream:", chunk.__error__);
      break;
    }

    console.log("Update:", chunk);
  }
} catch (error) {
  console.error("Stream error:", error);
}
```

### Async Streaming (Python)

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

### Streaming with Timeouts (TypeScript)

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [slowTool],
});

async function streamWithTimeout(timeoutMs: number) {
  const timeout = setTimeout(() => {
    throw new Error(`Stream timeout after ${timeoutMs}ms`);
  }, timeoutMs);

  try {
    for await (const chunk of await agent.stream(
      { messages: [{ role: "user", content: "Do something slow" }] },
      { streamMode: "updates" }
    )) {
      clearTimeout(timeout);
      console.log(chunk);

      // Reset timeout for next chunk
      timeout.setTimeout(() => {
        throw new Error(`Stream timeout after ${timeoutMs}ms`);
      }, timeoutMs);
    }
  } finally {
    clearTimeout(timeout);
  }
}
```

### Buffering Tokens for Display

#### Python

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

#### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

let buffer = "";
const stream = await model.stream("Write a long essay");

for await (const chunk of stream) {
  buffer += chunk.content;

  // Update UI every 10 characters or on complete words
  if (buffer.length >= 10 || chunk.content.includes(" ")) {
    console.log(buffer);
    buffer = "";
  }
}

// Flush remaining buffer
if (buffer) {
  console.log(buffer);
}
```

### Stream with Context Manager (Python)

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

- **Stream modes**: Choose which data to stream
- **Multiple modes**: Combine different stream types
- **Custom updates**: Emit user-defined progress data
- **Chunk processing**: Handle each chunk as needed
- **Error handling**: Catch and handle stream errors

### What You CANNOT Configure

- **Chunk size**: Determined by model/provider
- **Chunk timing**: Arrives as provider sends
- **Guarantee order**: Async streams may vary
- **Modify past chunks**: Chunks are immutable

## Gotchas

### 1. Tuple Unpacking for Messages Mode (Python)

```python
# ❌ Problem: Not unpacking messages mode
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    print(chunk.content)  # AttributeError!

# ✅ Solution: Messages mode returns (token, metadata) tuple
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)  # Correct!
```

### 2. Not Awaiting Stream (TypeScript)

```typescript
// ❌ Problem: Missing await
const stream = agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {  // Error: stream is Promise!
  console.log(chunk);
}

// ✅ Solution: Await stream initialization
const stream = await agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {
  console.log(chunk);
}
```

### 3. Stream Mode Confusion

#### Python

```python
# ❌ Problem: Using wrong mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk.content)  # AttributeError!

# ✅ Solution: Use "messages" mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)
```

#### TypeScript

```typescript
// ❌ Problem: Using wrong mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "updates" })) {
  console.log(chunk.content);  // Not how updates work!
}

// ✅ Solution: Use "messages" mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  const [token, metadata] = chunk;
  console.log(token.content);
}
```

### 4. Sync vs Async (Python)

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

### 5. Not Handling All Modes

#### Python

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

#### TypeScript

```typescript
// ❌ Problem: Not handling different modes
for await (const chunk of await agent.stream(
  input,
  { streamMode: ["updates", "messages"] }
)) {
  console.log(chunk);  // Which mode is this?
}

// ✅ Solution: Destructure mode
for await (const [mode, chunk] of await agent.stream(
  input,
  { streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    const [token, metadata] = chunk;
    console.log(token.content);
  } else if (mode === "updates") {
    console.log("Step:", chunk);
  }
}
```

### 6. Flush for Real-time Display (Python)

```python
# ❌ Problem: Output not appearing in real-time
for chunk in model.stream("Long response"):
    print(chunk.content)  # May be buffered

# ✅ Solution: Use flush=True
for chunk in model.stream("Long response"):
    print(chunk.content, end="", flush=True)  # Real-time display
```

### 7. Generator Exhaustion (Python)

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

### 8. Breaking Out of Stream Early (TypeScript)

```typescript
// ❌ Problem: Not properly cleaning up
for await (const chunk of await agent.stream(input)) {
  if (someCondition) {
    break;  // Stream may not clean up properly
  }
}

// ✅ Solution: Use try/finally or explicit cleanup
const stream = await agent.stream(input);
try {
  for await (const chunk of stream) {
    if (someCondition) {
      break;
    }
  }
} finally {
  // Cleanup if needed
}
```

## Links to Documentation

### Python
- [Streaming Overview](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- [LangGraph Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Model Streaming](https://docs.langchain.com/oss/python/langchain/models)
- [Human-in-the-Loop Streaming](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)

### TypeScript
- [Streaming Overview](https://docs.langchain.com/oss/javascript/langchain/streaming/overview)
- [LangGraph Streaming](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [Model Streaming](https://docs.langchain.com/oss/javascript/langchain/models)
- [Human-in-the-Loop Streaming](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
