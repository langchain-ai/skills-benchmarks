---
name: LangChain Streaming (TypeScript)
description: "[LangChain] Stream outputs from LangChain agents and models - includes stream modes, token streaming, progress updates, and real-time feedback"
---

<overview>
Streaming allows you to surface real-time updates from LangChain agents and models as they run. Instead of waiting for complete responses, you can display output progressively, improving user experience especially for long-running operations.

**Key Concepts:**
- **Stream Modes**: Different types of data streams (values, updates, messages, custom)
- **Token Streaming**: LLM tokens as they're generated
- **Agent Progress**: State updates after each agent step
- **Custom Updates**: User-defined progress signals
</overview>

<when-to-use>

| Scenario | Stream? | Why |
|----------|---------|-----|
| Long model responses | Yes | Show tokens as generated |
| Multi-step agent tasks | Yes | Show progress through steps |
| Long-running tools | Yes | Provide progress updates |
| Simple quick requests | Partial Maybe | Overhead might not be worth it |
| Backend batch processing | No | No user waiting for updates |

</when-to-use>

<stream-mode-selection>

| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state object |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | [token, metadata] tuples |
| `"custom"` | Need custom progress signals | User-defined data |
| Multiple modes | Need combined data | Array of modes |

</stream-mode-selection>

<ex-basic-model-token-streaming>
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
</ex-basic-model-token-streaming>

<ex-agent-progress-streaming>
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
</ex-agent-progress-streaming>

<ex-combined-streaming>
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
</ex-combined-streaming>

<ex-stream-with-values-mode>
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
</ex-stream-with-values-mode>

<ex-custom-progress-updates-from-tools>
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
</ex-custom-progress-updates-from-tools>

<ex-streaming-in-web-applications>
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
</ex-streaming-in-web-applications>

<ex-error-handling-in-streams>
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
</ex-error-handling-in-streams>

<ex-streaming-with-timeouts>
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
</ex-streaming-with-timeouts>

<ex-buffering-tokens-for-display>
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
</ex-buffering-tokens-for-display>

<boundaries>
**What You CAN Configure:**
- Stream modes: Choose which data to stream
- Multiple modes: Combine different stream types
- Custom updates: Emit user-defined progress data
- Chunk processing: Handle each chunk as needed
- Error handling: Catch and handle stream errors

**What You CANNOT Configure:**
- Chunk size: Determined by model/provider
- Chunk timing: Arrives as provider sends
- Guarantee order: Async streams may vary
- Modify past chunks: Chunks are immutable
</boundaries>

<fix-not-awaiting-stream>
```typescript
// WRONG: Problem: Missing await
const stream = agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {  // Error: stream is Promise!
  console.log(chunk);
}

// CORRECT: Solution: Await stream initialization
const stream = await agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {
  console.log(chunk);
}
```
</fix-not-awaiting-stream>

<fix-accessing-content-wrong>
```typescript
// WRONG: Problem: Wrong property for messages mode
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  console.log(chunk.content);  // undefined!
}

// CORRECT: Solution: Messages mode returns [token, metadata] tuple
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  const [token, metadata] = chunk;
  console.log(token.content);  // Correct!
}
```
</fix-accessing-content-wrong>

<fix-stream-mode-confusion>
```typescript
// WRONG: Problem: Using wrong mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "updates" })) {
  console.log(chunk.content);  // Not how updates work!
}

// CORRECT: Solution: Use "messages" mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  const [token, metadata] = chunk;
  console.log(token.content);
}
```
</fix-stream-mode-confusion>

<fix-breaking-out-of-stream-early>
```typescript
// WRONG: Problem: Not properly cleaning up
for await (const chunk of await agent.stream(input)) {
  if (someCondition) {
    break;  // Stream may not clean up properly
  }
}

// CORRECT: Solution: Use try/finally or explicit cleanup
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
</fix-breaking-out-of-stream-early>

<fix-mixing-stream-modes>
```typescript
// WRONG: Problem: Not handling different modes
for await (const chunk of await agent.stream(
  input,
  { streamMode: ["updates", "messages"] }
)) {
  console.log(chunk);  // Which mode is this?
}

// CORRECT: Solution: Destructure mode
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
</fix-mixing-stream-modes>

<documentation-links>
- [Streaming Overview](https://docs.langchain.com/oss/javascript/langchain/streaming/overview)
- [LangGraph Streaming](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [Model Streaming](https://docs.langchain.com/oss/javascript/langchain/models)
- [Human-in-the-Loop Streaming](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
</documentation-links>
