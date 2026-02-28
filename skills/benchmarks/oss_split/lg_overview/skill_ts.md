---
name: LangGraph Overview (TypeScript)
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
**Use LangGraph when you need:**
- Fine-grained control over agent orchestration
- Durable execution for long-running, stateful agents
- Complex workflows combining deterministic and agentic steps
- Production infrastructure for agent deployment
- Human-in-the-loop workflows
- Persistent state across multiple interactions

**Consider alternatives when you:**
- Need a quick start with pre-built architectures - Use **LangChain agents**
- Want batteries-included features (automatic compression, virtual filesystem) - Use **Deep Agents**
- Have simple, stateless LLM workflows - Use **LangChain** directly
- Don't need state persistence or complex orchestration
</when-to-use>

<decision-table>

| Requirement | Use LangGraph | Use LangChain | Use Deep Agents |
|------------|---------------|---------------|-----------------|
| Quick prototyping | No | Yes | Yes |
| Custom orchestration logic | Yes | No | Partial (limited) |
| Durable execution | Yes | Partial (via LangGraph) | Yes |
| Human-in-the-loop | Yes | Partial (via LangGraph) | Yes |
| State persistence | Yes | No | Yes |
| Production deployment | Yes | Partial (use with LangGraph) | Yes |
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

<ex-basic-langgraph-agent>
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
</ex-basic-langgraph-agent>

<ex-agent-with-persistence>
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
</ex-agent-with-persistence>

<ex-streaming-agent-responses>
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
</ex-streaming-agent-responses>

<boundaries>
**What Agents CAN Configure/Control:**
- Node Logic: Define any async function as a node
- State Schema: Customize state structure and reducers
- Control Flow: Add conditional edges, loops, branching
- Persistence Layer: Choose checkpointer (MemorySaver, SQLite, Postgres)
- Streaming Modes: Configure what data to stream
- Interrupts: Add human-in-the-loop at any point
- Recursion Limits: Control maximum execution steps
- Tools and Models: Use any LLM or tool provider

**What Agents CANNOT Configure/Control:**
- Core Graph Execution Model: Pregel-based runtime is fixed
- Super-step Behavior: Cannot change how nodes are batched
- Message Passing Protocol: Internal communication is predefined
- Checkpoint Schema: Internal checkpoint format is fixed
- Graph Compilation: Cannot modify compilation logic
</boundaries>

<fix-thread-ids-required-for-persistence>
```typescript
// WRONG: No thread_id with checkpointer
await agent.invoke({ messages: [...] });  // State not persisted!

// CORRECT: Always provide thread_id
await agent.invoke(
  { messages: [...] },
  { configurable: { thread_id: "user-123" } }
);
```
</fix-thread-ids-required-for-persistence>

<fix-state-updates-require-proper-reducers>
```typescript
// WRONG: Messages will be overwritten, not appended
const BadState = new StateSchema({
  messages: z.array(BaseMessageSchema),  // No reducer!
});

// CORRECT: Use MessagesValue for automatic message handling
import { MessagesValue } from "@langchain/langgraph";

const GoodState = new StateSchema({
  messages: MessagesValue,  // Handles message updates correctly
});
```
</fix-state-updates-require-proper-reducers>

<fix-compile-before-using>
```typescript
// WRONG: StateGraph is not executable
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke(...);  // Error!

// CORRECT: Must compile first
const graph = builder.compile();
await graph.invoke(...);
```
</fix-compile-before-using>

<fix-infinite-loops-need-termination>
```typescript
// WRONG: Loop without exit condition
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // Infinite loop!

// CORRECT: Add conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) {
    return END;
  }
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue);
```
</fix-infinite-loops-need-termination>

<fix-async-await-required>
```typescript
// WRONG: Forgetting await
const result = agent.invoke(...);  // Returns Promise!
console.log(result.messages);  // undefined

// CORRECT: Always await
const result = await agent.invoke(...);
console.log(result.messages);  // Works!
```
</fix-async-await-required>

<documentation-links>
**Installation:**
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

**Links:**
- [LangGraph Overview (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/overview)
- [LangGraph Quickstart](https://docs.langchain.com/oss/javascript/langgraph/quickstart)
- [Graph API Reference](https://docs.langchain.com/oss/javascript/langgraph/graph-api)
- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Streaming Guide](https://docs.langchain.com/oss/javascript/langgraph/streaming)
- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/javascript/releases/langgraph-v1)
</documentation-links>
