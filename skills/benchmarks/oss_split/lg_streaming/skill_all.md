---
name: LangGraph Streaming
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

<ex-values>
<python>
Full state after each step:

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
</python>

<typescript>
Full state after each step:

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
</typescript>
</ex-values>

<ex-updates>
<python>
Incremental state deltas:

```python
# Stream only the changes
for chunk in graph.stream(
    {"count": 0},
    stream_mode="updates"
):
    print(chunk)  # {"process": {"count": 1}}
```
</python>

<typescript>
Incremental state deltas:

```typescript
// Stream only the changes
for await (const chunk of await graph.stream(
  { count: 0 },
  { streamMode: "updates" }
)) {
  console.log(chunk);  // { process: { count: 1 } }
}
```
</typescript>
</ex-updates>

<ex-tokens>
<python>
Stream tokens as generated:

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
</python>

<typescript>
Stream tokens as generated:

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
</typescript>
</ex-tokens>

<ex-custom>
<python>
Emit custom data from nodes:

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
</python>

<typescript>
Emit custom data via writer:

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
</typescript>
</ex-custom>

<ex-multi>
<python>
Combine multiple stream modes:

```python
# Stream multiple modes simultaneously
for mode, chunk in graph.stream(
    {"messages": [HumanMessage("Hi")]},
    stream_mode=["updates", "messages", "custom"]
):
    print(f"{mode}: {chunk}")
```
</python>

<typescript>
Combine multiple stream modes:

```typescript
// Stream multiple modes simultaneously
for await (const [mode, chunk] of await graph.stream(
  { messages: [new HumanMessage("Hi")] },
  { streamMode: ["updates", "messages", "custom"] }
)) {
  console.log(`${mode}:`, chunk);
}
```
</typescript>
</ex-multi>

<ex-async>
<python>
Async streaming with astream:

```python
async for chunk in graph.astream(
    {"count": 0},
    stream_mode="values"
):
    print(chunk)
```
</python>
</ex-async>

<ex-subgraphs>
<python>
Stream from nested graphs:

```python
# Include subgraph outputs
for chunk in graph.stream(
    {"data": "test"},
    stream_mode="updates",
    subgraphs=True  # Stream from nested graphs too
):
    print(chunk)
```
</python>

<typescript>
Stream from nested graphs:

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
</typescript>
</ex-subgraphs>

<ex-interrupts>
<python>
Handle interrupts during streaming:

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
</python>

<typescript>
Handle interrupts during streaming:

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
</typescript>
</ex-interrupts>

<boundaries>
**What You CAN Configure**

- Choose stream modes
- Stream multiple modes simultaneously
- Emit custom data from nodes
- Stream from subgraphs
- Combine streaming with interrupts

**What You CANNOT Configure**

- Modify streaming protocol
- Change when checkpoints are created
- Alter token streaming format
</boundaries>

<fix-messages-mode-requires-llm>
<python>
LLM call required for token streaming:

```python
# WRONG - No LLM called, nothing streamed
def node(state):
    return {"output": "static text"}

for chunk in graph.stream({}, stream_mode="messages"):
    print(chunk)  # Nothing!

# CORRECT - LLM invoked
def node(state):
    response = model.invoke(state["messages"])  # LLM call
    return {"messages": [response]}
```
</python>

<typescript>
LLM call required for token streaming:

```typescript
// WRONG - No LLM called, nothing streamed
const node = async (state) => ({ output: "static text" });

for await (const chunk of await graph.stream({}, { streamMode: "messages" })) {
  console.log(chunk);  // Nothing!
}

// CORRECT - LLM invoked
const node = async (state) => {
  const response = await model.invoke(state.messages);  // LLM call
  return { messages: [response] };
};
```
</typescript>
</fix-messages-mode-requires-llm>

<fix-custom-mode-needs-stream-writer>
<python>
Use get_stream_writer for custom data:

```python
# WRONG - No writer, nothing streamed
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
</python>

<typescript>
Use config.writer for custom data:

```typescript
// WRONG - No writer, nothing streamed
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
</typescript>
</fix-custom-mode-needs-stream-writer>

<fix-stream-modes-are-arrays>
<python>
Use array for multiple modes:

```python
# WRONG - Single string
graph.stream({}, stream_mode="updates, messages")

# CORRECT - List
graph.stream({}, stream_mode=["updates", "messages"])
```
</python>

<typescript>
Use array for multiple modes:

```typescript
// WRONG - Single string with comma
await graph.stream({}, { streamMode: "updates, messages" });

// CORRECT - Array
await graph.stream({}, { streamMode: ["updates", "messages"] });
```
</typescript>
</fix-stream-modes-are-arrays>

<fix-async-stream-syntax>
<python>
Use async for with astream:

```python
# WRONG
for chunk in graph.astream({}):  # SyntaxError!
    print(chunk)

# CORRECT
async for chunk in graph.astream({}):
    print(chunk)
```
</python>

<typescript>
Await the stream call:

```typescript
// WRONG - Missing await
const stream = graph.stream({});
for await (const chunk of stream) {  // Error!
  console.log(chunk);
}

// CORRECT
for await (const chunk of await graph.stream({})) {
  console.log(chunk);
}
```
</typescript>
</fix-async-stream-syntax>

<links>
**Python**
- [Streaming Guide](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Stream Modes](https://docs.langchain.com/oss/python/langgraph/streaming#supported-stream-modes)
- [Custom Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)

**TypeScript**
- [Streaming Guide](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [Stream Modes](https://docs.langchain.com/oss/javascript/langgraph/streaming#supported-stream-modes)
</links>
