---
name: LangChain Agents (TypeScript)
description: [LangChain] Create and use LangChain agents with create_agent - includes agent loops, ReAct pattern, tool execution, and state management
---

# langchain-agents (JavaScript/TypeScript)

## Overview

Agents combine language models with tools to create systems that can reason about tasks, decide which tools to use, and iteratively work towards solutions. The `createAgent()` function provides a production-ready agent implementation built on LangGraph.

**Key Concepts:**
- **Agent Loop**: The model decides → calls tools → observes results → repeats until done
- **ReAct Pattern**: Reasoning and Acting - the agent reasons about what to do, then acts by calling tools
- **Graph-based Runtime**: Agents run on a LangGraph graph with nodes (model, tools, middleware) and edges

## When to Use Agents

| Scenario | Use Agent? | Why |
|----------|-----------|-----|
| Need to call external APIs/databases | ✅ Yes | Agents can dynamically choose which tools to call |
| Multi-step task with decision points | ✅ Yes | Agent loop handles iterative reasoning |
| Simple prompt-response | ❌ No | Use a chat model directly |
| Predetermined workflow | ❌ No | Use LangGraph workflow instead |
| Need tool calling without iteration | ⚠️ Maybe | Consider using model.bindTools() directly |

## Decision Tables

### Choosing Agent Configuration

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `createAgent({ model, tools })` | Search, calculator, weather |
| Custom system instructions | Add `systemPrompt` | Domain-specific behavior |
| Human approval for sensitive operations | Add `humanInTheLoopMiddleware` | Database writes, emails |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |
| Structured output format | Add `responseFormat` | Extract contact info, parse forms |

### Tool Strategy

| Tool Type | When to Use | Example |
|-----------|-------------|---------|
| Static tools | Tools don't change during execution | Search, weather, calculator |
| Dynamic tools | Tools depend on runtime state | User-specific APIs |
| Built-in tools | Need common functionality | File system, code execution |
| Custom tools | Domain-specific operations | Your business logic |

## Code Examples

### Basic Agent with Tools

```typescript
import { createAgent } from "langchain";
import { tool } from "langchain";

// Define tools
const searchTool = tool(
  async ({ query }: { query: string }) => {
    // Your search implementation
    return `Results for: ${query}`;
  },
  {
    name: "search",
    description: "Search for information on the web",
    schema: z.object({
      query: z.string().describe("The search query"),
    }),
  }
);

const weatherTool = tool(
  async ({ location }: { location: string }) => {
    return `Weather in ${location}: Sunny, 72°F`;
  },
  {
    name: "get_weather",
    description: "Get current weather for a location",
    schema: z.object({
      location: z.string().describe("City name"),
    }),
  }
);

// Create agent
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, weatherTool],
});

// Invoke agent
const result = await agent.invoke({
  messages: [
    { role: "user", content: "What's the weather in San Francisco?" }
  ],
});

console.log(result.messages[result.messages.length - 1].content);
```

### Agent with System Prompt

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
  systemPrompt: `You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.`,
});
```

### Agent Loop Execution Flow

```typescript
// The agent runs in a loop:
// 1. Model receives user message
// 2. Model decides to call a tool (or finish)
// 3. Tool executes and returns result
// 4. Result goes back to model
// 5. Repeat until model decides to finish

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, weatherTool],
});

// This single invoke() call handles the entire loop
const result = await agent.invoke({
  messages: [
    { 
      role: "user", 
      content: "Search for the capital of France, then get its weather" 
    }
  ],
});

// Agent automatically:
// - Calls search tool for capital
// - Receives "Paris"
// - Calls weather tool for Paris
// - Receives weather data
// - Responds with final answer
```

### Streaming Agent Progress

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Stream with updates mode to see each step
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for LangChain" }] },
  { streamMode: "updates" }
)) {
  console.log("Step:", chunk);
}

// Stream with messages mode for LLM tokens
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for LangChain" }] },
  { streamMode: "messages" }
)) {
  const [token, metadata] = chunk;
  if (token.content) {
    process.stdout.write(token.content);
  }
}
```

### Agent with Persistence

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  checkpointer,
});

// First conversation
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({
  messages: [{ role: "user", content: "My name is Alice" }]
}, config);

// Later conversation - agent remembers
await agent.invoke({
  messages: [{ role: "user", content: "What's my name?" }]
}, config);
// Response: "Your name is Alice"
```

### Multiple Tool Calls in Parallel

```typescript
// Models can call multiple tools simultaneously
const agent = createAgent({
  model: "gpt-4.1",
  tools: [weatherTool, newsToolTool],
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Get weather for NYC and latest news for SF"
  }],
});

// Agent may call both tools in parallel in a single step
```

### Dynamic Tools (Runtime-Dependent)

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: (state) => {
    // Tools can depend on current state
    const userId = state.config?.configurable?.user_id;
    return [
      getUserSpecificTool(userId),
      commonTool,
    ];
  },
});
```

### Error Handling in Agents

```typescript
import { createAgent, wrapToolCall } from "langchain";

// Custom error handling middleware
const errorHandler = wrapToolCall({
  name: "ErrorHandler",
  wrapToolCall: async (toolCall, handler) => {
    try {
      return await handler(toolCall);
    } catch (error) {
      return {
        ...toolCall,
        content: `Tool error: ${error.message}`,
      };
    }
  },
});

const agent = createAgent({
  model: "gpt-4.1",
  tools: [riskyTool],
  middleware: [errorHandler],
});
```

## Boundaries

### What Agents CAN Configure

✅ **Model**: Any chat model (OpenAI, Anthropic, Google, etc.)
✅ **Tools**: Custom tools, built-in tools, dynamic tools
✅ **System Prompt**: Instructions for agent behavior
✅ **Middleware**: Human-in-the-loop, error handling, logging
✅ **Checkpointer**: Memory/persistence across conversations
✅ **Response Format**: Structured output schemas
✅ **Max Iterations**: Prevent infinite loops

### What Agents CANNOT Configure

❌ **Direct Graph Structure**: Use LangGraph directly for custom flows
❌ **Tool Execution Order**: Model decides which tools to call
❌ **Interrupt Model Decision**: Can only interrupt before tool execution
❌ **Multiple Models**: One agent = one model (use subagents for multiple)

## Gotchas

### 1. Agent Doesn't Stop (Infinite Loop)

```typescript
// ❌ Problem: No clear stopping condition
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

await agent.invoke({
  messages: [{ role: "user", content: "Keep searching until perfect" }]
});

// ✅ Solution: Set max iterations
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  maxIterations: 10, // Stop after 10 tool calls
});
```

### 2. Tool Not Being Called

```typescript
// ❌ Problem: Vague tool description
const badTool = tool(
  async ({ input }: { input: string }) => "result",
  {
    name: "tool",
    description: "Does stuff", // Too vague!
    schema: z.object({ input: z.string() }),
  }
);

// ✅ Solution: Clear, specific descriptions
const goodTool = tool(
  async ({ query }: { query: string }) => "result",
  {
    name: "web_search",
    description: "Search the web for current information about a topic. Use this when you need recent data that wasn't in your training.",
    schema: z.object({
      query: z.string().describe("The search query (2-10 words)"),
    }),
  }
);
```

### 3. State Not Persisting

```typescript
// ❌ Problem: No checkpointer
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Each invoke is isolated - no memory
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember "Bob"

// ✅ Solution: Add checkpointer and thread_id
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Bob"
```

### 4. Messages vs State Confusion

```typescript
// Agent state includes more than just messages
const result = await agent.invoke({
  messages: [{ role: "user", content: "Hello" }]
});

// ✅ Access full conversation history
console.log(result.messages); // Array of all messages

// ✅ Access structured output (if configured)
console.log(result.structuredResponse);

// ❌ Don't try to access result.content directly
// console.log(result.content); // undefined!
```

### 5. Tool Results Must Be Serializable

```typescript
// ❌ Problem: Returning non-serializable objects
const badTool = tool(
  async () => {
    return new Date(); // Date objects aren't JSON-serializable by default
  },
  { name: "get_time", description: "Get current time" }
);

// ✅ Solution: Return serializable data
const goodTool = tool(
  async () => {
    return new Date().toISOString(); // String is serializable
  },
  { name: "get_time", description: "Get current time" }
);
```

### 6. Streaming Modes Matter

```typescript
// Different stream modes show different information

// "values" - Full state after each step
for await (const chunk of await agent.stream(input, { streamMode: "values" })) {
  console.log(chunk.messages); // All messages so far
}

// "updates" - Only what changed in each step
for await (const chunk of await agent.stream(input, { streamMode: "updates" })) {
  console.log(chunk); // Just the delta
}

// "messages" - LLM token stream
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  const [token, metadata] = chunk;
  console.log(token.content); // Each token
}
```

## Links to Documentation

- [Agents Overview](https://docs.langchain.com/oss/javascript/langchain/agents)
- [createAgent API Reference](https://docs.langchain.com/oss/javascript/releases/langchain-v1)
- [LangGraph Concepts](https://docs.langchain.com/oss/javascript/langgraph/workflows-agents)
- [Tool Calling Guide](https://docs.langchain.com/oss/javascript/langchain/tools)
- [Streaming Guide](https://docs.langchain.com/oss/javascript/langchain/streaming/overview)
- [Human-in-the-Loop](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
