---
name: LangGraph Streaming (TypeScript)
description: "[LangGraph] Streaming real-time updates from LangGraph: stream modes (values, updates, messages, custom, debug) for responsive UX"
---

<overview>
LangGraph's streaming system surfaces real-time updates during graph execution, crucial for responsive LLM applications. Stream graph state, LLM tokens, or custom data as it's generated.
</overview>

<decision-table>

| Mode | What it Streams | Use Case |
|------|----------------|----------|
| `values` | Full state after each step | Monitor complete state changes |
| `updates` | State deltas after each step | Track incremental updates |
| `messages` | LLM tokens + metadata | Chat UIs, token streaming |
| `custom` | User-defined data | Progress indicators, logs |
| `debug` | All execution details | Debugging, detailed tracing |

</decision-table>

<ex-stream-state-values>
```typescript
import { StateGraph, START, END } from "@langchain/langgraph";

const process = async (state) => ({  count: state.count + 1 });

const graph = new StateGraph(State)
  .addNode("process", process)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile();

// Stream full state after each step
for await (const chunk of await graph.stream(
  { count: 0 },
  { streamMode: "values" }
)) {
  console.log(chunk);  // { count: 0 }, then { count: 1 }
}
```
</ex-stream-state-values>

<ex-stream-state-updates-deltas>
```typescript
// Stream only the changes
for await (const chunk of await graph.stream(
  { count: 0 },
  { streamMode: "updates" }
)) {
  console.log(chunk);  // { process: { count: 1 } }
}
```
</ex-stream-state-updates-deltas>

<ex-stream-llm-tokens>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";

const model = new ChatOpenAI({ model: "gpt-4" });

const llmNode = async (state) => {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
};

const graph = new StateGraph(State)
  .addNode("llm", llmNode)
  .compile();

// Stream LLM tokens as they're generated
for await (const chunk of await graph.stream(
  { messages: [new HumanMessage("Hello")] },
  { streamMode: "messages" }
)) {
  const [token, metadata] = chunk;
  if (token.content) {
    process.stdout.write(token.content);
  }
}
```
</ex-stream-llm-tokens>

<ex-stream-custom-data>
```typescript
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const myNode = async (state, config: LangGraphRunnableConfig) => {
  const writer = config.writer;

  // Emit custom updates
  writer?.("Processing step 1...");
  // Do work
  writer?.("Processing step 2...");
  // More work
  writer?.("Complete!");

  return { result: "done" };
};

const graph = new StateGraph(State)
  .addNode("work", myNode)
  .compile();

for await (const chunk of await graph.stream(
  { data: "test" },
  { streamMode: "custom" }
)) {
  console.log(chunk);  // "Processing step 1...", etc.
}
```
</ex-stream-custom-data>

<ex-multiple-stream-modes>
```typescript
// Stream multiple modes simultaneously
for await (const [mode, chunk] of await graph.stream(
  { messages: [new HumanMessage("Hi")] },
  { streamMode: ["updates", "messages", "custom"] }
)) {
  console.log(`${mode}:`, chunk);
}
```
</ex-multiple-stream-modes>

<ex-stream-with-subgraphs>
```typescript
// Include subgraph outputs
for await (const chunk of await graph.stream(
  { data: "test" },
  {
    streamMode: "updates",
    subgraphs: true  // Stream from nested graphs too
  }
)) {
  console.log(chunk);
}
```
</ex-stream-with-subgraphs>

<ex-stream-with-interrupts>
```typescript
const config = {
  configurable: { thread_id: "1" },
  streamMode: ["messages", "updates"] as const,
  subgraphs: true
};

for await (const [metadata, mode, chunk] of await graph.stream(
  { query: "test" },
  config
)) {
  if (mode === "messages") {
    // Handle streaming LLM content
    const [msg, _] = chunk;
    if (msg.content) {
      process.stdout.write(msg.content);
    }
  } else if (mode === "updates") {
    // Check for interrupts
    if ("__interrupt__" in chunk) {
      // Handle interrupt
      const interruptInfo = chunk.__interrupt__[0].value;
      // Get user input and resume
      break;
    }
  }
}
```
</ex-stream-with-interrupts>

<boundaries>
**What You CAN Configure:**
- Choose stream modes
- Stream multiple modes simultaneously
- Emit custom data from nodes
- Stream from subgraphs
- Combine streaming with interrupts

**What You CANNOT Configure:**
- Modify streaming protocol
- Change when checkpoints are created
- Alter token streaming format
</boundaries>

<fix-messages-mode-requires-llm-invocation>
```typescript
// WRONG: No LLM called, nothing streamed
const node = async (state) => ({ output: "static text" });

for await (const chunk of await graph.stream({}, { streamMode: "messages" })) {
  console.log(chunk);  // Nothing!
}

// CORRECT: LLM invoked
const node = async (state) => {
  const response = await model.invoke(state.messages);  // LLM call
  return { messages: [response] };
};
```
</fix-messages-mode-requires-llm-invocation>

<fix-custom-mode-needs-writer>
```typescript
// WRONG: No writer, nothing streamed
const node = async (state) => {
  console.log("Processing...");  // Not streamed!
  return { data: "done" };
};

// CORRECT
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const node = async (state, config: LangGraphRunnableConfig) => {
  config.writer?.("Processing...");  // Streamed!
  return { data: "done" };
};
```
</fix-custom-mode-needs-writer>

<fix-stream-modes-are-arrays>
```typescript
// WRONG: Single string with comma
await graph.stream({}, { streamMode: "updates, messages" });

// CORRECT: Array
await graph.stream({}, { streamMode: ["updates", "messages"] });
```
</fix-stream-modes-are-arrays>

<fix-always-await-stream>
```typescript
// WRONG: Missing await
const stream = graph.stream({});
for await (const chunk of stream) {  // Error!
  console.log(chunk);
}

// CORRECT
for await (const chunk of await graph.stream({})) {
  console.log(chunk);
}
```
</fix-always-await-stream>

<documentation-links>
- [Streaming Guide](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [Stream Modes](https://docs.langchain.com/oss/javascript/langgraph/streaming#supported-stream-modes)
</documentation-links>
