---
name: LangGraph Overview
description: "[LangGraph] Understanding LangGraph: A low-level orchestration framework for building stateful, long-running agents with durable execution, streaming, and human-in-the-loop capabilities"
---

<overview>
LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It is trusted by companies like Klarna, Replit, and Elastic for production agent workloads.

**Key Characteristics:**
- **Low-level control**: Direct control over agent orchestration without high-level abstractions
- **Stateful execution**: Built-in state management and persistence
- **Production-ready**: Durable execution, streaming, human-in-the-loop, and fault-tolerance
- **Framework agnostic**: Works standalone or with LangChain components
</overview>

<when-to-use>
**When to Use LangGraph**

LangGraph is ideal when you need:
- Fine-grained control over agent orchestration
- Durable execution for long-running, stateful agents
- Complex workflows combining deterministic and agentic steps
- Production infrastructure for agent deployment
- Human-in-the-loop workflows
- Persistent state across multiple interactions

**When NOT to Use LangGraph**

Consider alternatives when you:
- Need a quick start with pre-built architectures -> Use **LangChain agents**
- Want batteries-included features (automatic compression, virtual filesystem) -> Use **Deep Agents**
- Have simple, stateless LLM workflows -> Use **LangChain LCEL**
- Don't need state persistence or complex orchestration
</when-to-use>

<decision-table>
| Requirement | Use LangGraph | Use LangChain | Use Deep Agents |
|------------|---------------|---------------|-----------------|
| Quick prototyping | No | Yes | Yes |
| Custom orchestration logic | Yes | No | Limited |
| Durable execution | Yes | Via LangGraph | Yes |
| Human-in-the-loop | Yes | Via LangGraph | Yes |
| State persistence | Yes | No | Yes |
| Production deployment | Yes | Use with LangGraph | Yes |
| Learning curve | High | Low | Medium |
</decision-table>

<key-concepts>
**1. Graph-Based Execution Model**

LangGraph models agent workflows as **graphs** with three core components:

- **State**: Shared data structure representing the current snapshot of your application
- **Nodes**: Functions that encode agent logic and update state
- **Edges**: Determine which node executes next (can be conditional or fixed)

**2. Core Capabilities**

| Capability | Description |
|-----------|-------------|
| **Durable Execution** | Agents persist through failures and resume from checkpoints |
| **Streaming** | Real-time updates during execution (state, tokens, custom data) |
| **Human-in-the-loop** | Pause execution for human review and intervention |
| **Persistence** | Thread-level and cross-thread state management |
| **Time Travel** | Resume from any checkpoint in execution history |

**3. Message Passing Model**

Inspired by Google's Pregel system:
- Execution proceeds in discrete "super-steps"
- Nodes execute in parallel within a super-step
- Sequential nodes belong to separate super-steps
- Graph terminates when all nodes are inactive
</key-concepts>

<ex-basic-agent>
<python>
Tool-calling agent with routing:

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

# 1. Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# 2. Initialize model with tools
model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)
tools = [add, multiply]
model_with_tools = model.bind_tools(tools)

# 3. Define state
class MessagesState(TypedDict):
    messages: Annotated[list, operator.add]
    llm_calls: int

# 4. Define nodes
def llm_call(state: dict):
    """LLM decides whether to call a tool or not."""
    return {
        "messages": [
            model_with_tools.invoke([
                SystemMessage(content="You are a helpful assistant."),
                *state["messages"]
            ])
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Execute tool calls."""
    result = []
    tools_by_name = {tool.name: tool for tool in tools}
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# 5. Define routing logic
def should_continue(state: MessagesState):
    """Route to tool_node or END."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return END

# 6. Build and compile graph
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    .add_edge("tool_node", "llm_call")
    .compile()
)

# 7. Invoke the agent
messages = agent.invoke({"messages": [HumanMessage(content="What is 3 * 4?")]})
for m in messages["messages"]:
    m.pretty_print()
```
</python>

<typescript>
Tool-calling agent with routing:

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";
import { SystemMessage, HumanMessage, AIMessage, ToolMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

// 1. Define tools
const multiply = tool(({ a, b }) => a * b, {
  name: "multiply",
  description: "Multiply two numbers",
  schema: z.object({
    a: z.number().describe("First number"),
    b: z.number().describe("Second number"),
  }),
});

const add = tool(({ a, b }) => a + b, {
  name: "add",
  description: "Add two numbers",
  schema: z.object({
    a: z.number().describe("First number"),
    b: z.number().describe("Second number"),
  }),
});

// 2. Initialize model with tools
const model = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
});

const toolsByName = { [add.name]: add, [multiply.name]: multiply };
const tools = Object.values(toolsByName);
const modelWithTools = model.bindTools(tools);

// 3. Define state
const MessagesState = new StateSchema({
  messages: MessagesValue,
  llmCalls: new ReducedValue(
    z.number().default(0),
    { reducer: (x, y) => x + y }
  ),
});

// 4. Define nodes
const llmCall = async (state) => {
  const response = await modelWithTools.invoke([
    new SystemMessage("You are a helpful assistant."),
    ...state.messages,
  ]);
  return {
    messages: [response],
    llmCalls: 1,
  };
};

const toolNode = async (state) => {
  const lastMessage = state.messages.at(-1);

  if (lastMessage == null || !AIMessage.isInstance(lastMessage)) {
    return { messages: [] };
  }

  const result = [];
  for (const toolCall of lastMessage.tool_calls ?? []) {
    const tool = toolsByName[toolCall.name];
    const observation = await tool.invoke(toolCall);
    result.push(observation);
  }
  return { messages: result };
};

// 5. Define routing logic
const shouldContinue = (state) => {
  const lastMessage = state.messages.at(-1);

  if (!lastMessage || !AIMessage.isInstance(lastMessage)) {
    return END;
  }

  if (lastMessage.tool_calls?.length) {
    return "toolNode";
  }
  return END;
};

// 6. Build and compile graph
const agent = new StateGraph(MessagesState)
  .addNode("llmCall", llmCall)
  .addNode("toolNode", toolNode)
  .addEdge(START, "llmCall")
  .addConditionalEdges("llmCall", shouldContinue, ["toolNode", END])
  .addEdge("toolNode", "llmCall")
  .compile();

// 7. Invoke the agent
const result = await agent.invoke({
  messages: [new HumanMessage("What is 3 * 4?")],
});

for (const message of result.messages) {
  console.log(`[${message._getType()}]: ${message.content}`);
}
```
</typescript>
</ex-basic-agent>

<ex-persistence>
<python>
Enable state persistence with checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

# Create checkpointer for state persistence
checkpointer = InMemorySaver()

# Compile with checkpointer
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue)
    .add_edge("tool_node", "llm_call")
    .compile(checkpointer=checkpointer)  # Add checkpointer
)

# First conversation turn
config = {"configurable": {"thread_id": "1"}}
agent.invoke(
    {"messages": [HumanMessage(content="Hi, I'm Alice")]},
    config
)

# Second turn - agent remembers context
agent.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config
)
```
</python>

<typescript>
Enable state persistence with checkpointer:

```typescript
import { MemorySaver } from "@langchain/langgraph";

// Create checkpointer for state persistence
const checkpointer = new MemorySaver();

// Compile with checkpointer
const agent = new StateGraph(MessagesState)
  .addNode("llmCall", llmCall)
  .addNode("toolNode", toolNode)
  .addEdge(START, "llmCall")
  .addConditionalEdges("llmCall", shouldContinue, ["toolNode", END])
  .addEdge("toolNode", "llmCall")
  .compile({ checkpointer });  // Add checkpointer

// First conversation turn
const config = { configurable: { thread_id: "1" } };
await agent.invoke(
  { messages: [new HumanMessage("Hi, I'm Alice")] },
  config
);

// Second turn - agent remembers context
await agent.invoke(
  { messages: [new HumanMessage("What's my name?")] },
  config
);
```
</typescript>
</ex-persistence>

<ex-streaming>
<python>
Stream state updates and tokens:

```python
# Stream state updates
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Calculate 5 + 3")]},
    stream_mode="updates"
):
    print(chunk)

# Stream LLM tokens
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Hello!")]},
    stream_mode="messages"
):
    print(chunk)

# Multiple stream modes
for mode, chunk in agent.stream(
    {"messages": [HumanMessage(content="Help me")]},
    stream_mode=["updates", "messages"]
):
    print(f"{mode}: {chunk}")
```
</python>

<typescript>
Stream state updates and tokens:

```typescript
// Stream state updates
for await (const chunk of await agent.stream(
  { messages: [new HumanMessage("Calculate 5 + 3")] },
  { streamMode: "updates" }
)) {
  console.log(chunk);
}

// Stream LLM tokens
for await (const chunk of await agent.stream(
  { messages: [new HumanMessage("Hello!")] },
  { streamMode: "messages" }
)) {
  console.log(chunk);
}

// Multiple stream modes
for await (const [mode, chunk] of await agent.stream(
  { messages: [new HumanMessage("Help me")] },
  { streamMode: ["updates", "messages"] }
)) {
  console.log(`${mode}:`, chunk);
}
```
</typescript>
</ex-streaming>

<boundaries>
**What Agents CAN Configure/Control**

- **Node Logic**: Define any function as a node
- **State Schema**: Customize state structure and reducers
- **Control Flow**: Add conditional edges, loops, branching
- **Persistence Layer**: Choose checkpointer (InMemory/MemorySaver, SQLite, Postgres)
- **Streaming Modes**: Configure what data to stream
- **Interrupts**: Add human-in-the-loop at any point
- **Recursion Limits**: Control maximum execution steps
- **Tools and Models**: Use any LLM or tool provider

**What Agents CANNOT Configure/Control**

- **Core Graph Execution Model**: Pregel-based runtime is fixed
- **Super-step Behavior**: Cannot change how nodes are batched
- **Message Passing Protocol**: Internal communication is predefined
- **Checkpoint Schema**: Internal checkpoint format is fixed
- **Graph Compilation**: Cannot modify compilation logic
</boundaries>

<fix-thread-id-required>
<python>
Provide thread_id for persistence:

```python
# WRONG - No thread_id with checkpointer
agent.invoke({"messages": [...]})  # State not persisted!

# CORRECT - Always provide thread_id
agent.invoke(
    {"messages": [...]},
    {"configurable": {"thread_id": "user-123"}}
)
```
</python>
<typescript>
Provide thread_id for persistence:

```typescript
// WRONG - No thread_id with checkpointer
await agent.invoke({ messages: [...] });  // State not persisted!

// CORRECT - Always provide thread_id
await agent.invoke(
  { messages: [...] },
  { configurable: { thread_id: "user-123" } }
);
```
</typescript>
</fix-thread-id-required>

<fix-state-reducers>
<python>
Use reducers for list accumulation:

```python
# WRONG - Messages will be overwritten, not appended
class State(TypedDict):
    messages: list  # No reducer!

# CORRECT - Use reducer to append
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]  # Appends messages
```
</python>
<typescript>
Use MessagesValue for message handling:

```typescript
// WRONG - Messages will be overwritten, not appended
const BadState = new StateSchema({
  messages: z.array(BaseMessageSchema),  // No reducer!
});

// CORRECT - Use MessagesValue for automatic message handling
import { MessagesValue } from "@langchain/langgraph";

const GoodState = new StateSchema({
  messages: MessagesValue,  // Handles message updates correctly
});
```
</typescript>
</fix-state-reducers>

<fix-compile-before-using>
<python>
Compile graph before invoking:

```python
# WRONG - StateGraph is not executable
builder = StateGraph(State).add_node("node", func)
builder.invoke(...)  # Error!

# CORRECT - Must compile first
graph = builder.compile()
graph.invoke(...)
```
</python>
<typescript>
Compile graph before invoking:

```typescript
// WRONG - StateGraph is not executable
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke(...);  // Error!

// CORRECT - Must compile first
const graph = builder.compile();
await graph.invoke(...);
```
</typescript>
</fix-compile-before-using>

<fix-infinite-loops>
<python>
Add conditional exit to loops:

```python
# WRONG - Loop without exit condition
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # Infinite loop!

# CORRECT - Add conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
</python>
<typescript>
Add conditional exit to loops:

```typescript
// WRONG - Loop without exit condition
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // Infinite loop!

// CORRECT - Add conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) {
    return END;
  }
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue);
```
</typescript>
</fix-infinite-loops>

<fix-langgraph-vs-langchain>
<python>
LangGraph for control, LangChain for simplicity:

```python
# LangChain (high-level, quick start)
from langchain.agents import create_agent
agent = create_agent(model, tools=[...])  # Simple, opinionated

# LangGraph (low-level, full control)
from langgraph.graph import StateGraph
graph = StateGraph(...).add_node(...).compile()  # More code, more control
```
</python>
</fix-langgraph-vs-langchain>

<fix-async-await>
<typescript>
Always await async invocations:

```typescript
// WRONG - Forgetting await
const result = agent.invoke(...);  // Returns Promise!
console.log(result.messages);  // undefined

// CORRECT - Always await
const result = await agent.invoke(...);
console.log(result.messages);  // Works!
```
</typescript>
</fix-async-await>

<installation>
**Python**

Install LangGraph and dependencies:

```bash
# Python
pip install -U langgraph

# With LangChain (optional but common)
pip install -U langchain

# Production persistence
pip install -U langgraph-checkpoint-postgres
```

**TypeScript**

Install LangGraph and dependencies:

```bash
# npm
npm install @langchain/langgraph

# yarn
yarn add @langchain/langgraph

# pnpm
pnpm add @langchain/langgraph

# With LangChain (optional but common)
npm install @langchain/core

# Production persistence
npm install @langchain/langgraph-checkpoint-postgres
```
</installation>

<links>
**Python**
- [LangGraph Overview (Python)](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [Graph API Reference](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Persistence Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Streaming Guide](https://docs.langchain.com/oss/python/langgraph/streaming)
- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)

**TypeScript**
- [LangGraph Overview (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/overview)
- [LangGraph Quickstart](https://docs.langchain.com/oss/javascript/langgraph/quickstart)
- [Graph API Reference](https://docs.langchain.com/oss/javascript/langgraph/graph-api)
- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Streaming Guide](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/javascript/releases/langgraph-v1)
</links>
