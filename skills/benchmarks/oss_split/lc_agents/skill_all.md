---
name: LangChain Agents
description: "[LangChain] Create and use LangChain agents with create_agent - includes agent loops, ReAct pattern, tool execution, and state management"
---

## Overview

Agents combine language models with tools to create systems that can reason about tasks, decide which tools to use, and iteratively work towards solutions. The `create_agent()`/`createAgent()` function provides a production-ready agent implementation built on LangGraph.

**Key Concepts:**
- **Agent Loop**: The model decides → calls tools → observes results → repeats until done
- **ReAct Pattern**: Reasoning and Acting - the agent reasons about what to do, then acts by calling tools
- **Graph-based Runtime**: Agents run on a LangGraph graph with nodes (model, tools, middleware) and edges

## When to Use Agents

| Scenario | Use Agent? | Why |
|----------|-----------|-----|
| Need to call external APIs/databases | Yes | Agents can dynamically choose which tools to call |
| Multi-step task with decision points | Yes | Agent loop handles iterative reasoning |
| Simple prompt-response | No | Use a chat model directly |
| Predetermined workflow | No | Use LangGraph workflow instead |
| Need tool calling without iteration | Maybe | Consider using model.bind_tools() directly |

## Decision Tables

### Choosing Agent Configuration

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `create_agent(model, tools)` | Search, calculator, weather |
| Custom system instructions | Add `system_prompt` | Domain-specific behavior |
| Human approval for sensitive operations | Add human-in-the-loop middleware | Database writes, emails |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |
| Structured output format | Add `response_format` | Extract contact info, parse forms |

### Tool Strategy

| Tool Type | When to Use | Example |
|-----------|-------------|---------|
| Static tools | Tools don't change during execution | Search, weather, calculator |
| Dynamic tools | Tools depend on runtime state | User-specific APIs |
| Built-in tools | Need common functionality | File system, code execution |
| Custom tools | Domain-specific operations | Your business logic |

## Code Examples

### Basic Agent with Tools

#### Python

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(model="gpt-4.1", tools=[search, get_weather])

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]
})
print(result["messages"][-1].content)
```

#### TypeScript

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const searchTool = tool(
  async ({ query }: { query: string }) => `Results for: ${query}`,
  {
    name: "search",
    description: "Search for information on the web",
    schema: z.object({ query: z.string().describe("The search query") }),
  }
);

const weatherTool = tool(
  async ({ location }: { location: string }) => `Weather in ${location}: Sunny, 72°F`,
  {
    name: "get_weather",
    description: "Get current weather for a location",
    schema: z.object({ location: z.string().describe("City name") }),
  }
);

const agent = createAgent({ model: "gpt-4.1", tools: [searchTool, weatherTool] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in San Francisco?" }],
});
console.log(result.messages[result.messages.length - 1].content);
```

### Agent with System Prompt

#### Python

```python
agent = create_agent(
    model="gpt-4.1",
    tools=[search, calculator],
    system_prompt="""You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.""",
)
```

#### TypeScript

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
  systemPrompt: `You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.`,
});
```

### Agent Loop Execution Flow

The agent runs in a loop:
1. Model receives user message
2. Model decides to call a tool (or finish)
3. Tool executes and returns result
4. Result goes back to model
5. Repeat until model decides to finish

#### Python

```python
agent = create_agent(model="gpt-4.1", tools=[search, get_weather])

# This single invoke() handles the entire loop
result = agent.invoke({
    "messages": [{"role": "user", "content": "Search for the capital of France, then get its weather"}]
})
# Agent automatically calls search → gets "Paris" → calls weather → responds
```

#### TypeScript

```typescript
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool, weatherTool] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for the capital of France, then get its weather" }],
});
```

### Streaming Agent Progress

#### Python

```python
# Stream with updates mode to see each step
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for LangChain"}]},
    stream_mode=["updates"],
):
    print(f"Step: {chunk}")

# Stream with messages mode for LLM tokens
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for LangChain"}]},
    stream_mode=["messages"],
):
    token, metadata = chunk
    if token.content:
        print(token.content, end="", flush=True)
```

#### TypeScript

```typescript
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
  if (token.content) process.stdout.write(token.content);
}
```

### Agent with Persistence

#### Python

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_agent(model="gpt-4.1", tools=[search], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)

# Later conversation - agent remembers
result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Response: "Your name is Alice"
```

#### TypeScript

```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool], checkpointer });

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);

// Later conversation - agent remembers
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Response: "Your name is Alice"
```

### Dynamic Tools (Runtime-Dependent)

#### Python

```python
def get_tools(state):
    """Tools can depend on current state."""
    user_id = state.get("config", {}).get("configurable", {}).get("user_id")
    return [get_user_specific_tool(user_id), common_tool]

agent = create_agent(model="gpt-4.1", tools=get_tools)  # Pass function instead of list
```

#### TypeScript

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: (state) => {
    const userId = state.config?.configurable?.user_id;
    return [getUserSpecificTool(userId), commonTool];
  },
});
```

### Tool with Type Hints / Schema

#### Python

```python
from langchain.tools import tool
from typing import Literal

@tool
def calculate(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> float:
    """Perform a mathematical calculation.

    Args:
        operation: The operation to perform
        a: First number
        b: Second number
    """
    ops = {"add": lambda: a + b, "subtract": lambda: a - b, "multiply": lambda: a * b, "divide": lambda: a / b}
    return ops[operation]()
```

#### TypeScript

```typescript
const calculatorTool = tool(
  async ({ operation, a, b }: { operation: string; a: number; b: number }) => {
    const ops: Record<string, () => number> = {
      add: () => a + b, subtract: () => a - b, multiply: () => a * b, divide: () => a / b,
    };
    return ops[operation]();
  },
  {
    name: "calculate",
    description: "Perform a mathematical calculation",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```

### Multiple Tool Calls in Parallel

#### Python

```python
# Models can call multiple tools simultaneously
agent = create_agent(
    model="gpt-4.1",
    tools=[get_weather, get_news],
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Get weather for NYC and latest news for SF"
    }]
})

# Agent may call both tools in parallel in a single step
```

#### TypeScript

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

### Error Handling in Agents

#### Python

```python
from langchain.agents import create_agent, wrap_tool_call

# Custom error handling middleware
@wrap_tool_call
async def error_handler(tool_call, handler):
    try:
        return await handler(tool_call)
    except Exception as error:
        return {
            **tool_call,
            "content": f"Tool error: {str(error)}",
        }

agent = create_agent(
    model="gpt-4.1",
    tools=[risky_tool],
    middleware=[error_handler],
)
```

#### TypeScript

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

- **Model**: Any chat model (OpenAI, Anthropic, Google, etc.)
- **Tools**: Custom tools, built-in tools, dynamic tools
- **System Prompt**: Instructions for agent behavior
- **Middleware**: Human-in-the-loop, error handling, logging
- **Checkpointer**: Memory/persistence across conversations
- **Response Format**: Structured output schemas
- **Max Iterations**: Prevent infinite loops

### What Agents CANNOT Configure

- **Direct Graph Structure**: Use LangGraph directly for custom flows
- **Tool Execution Order**: Model decides which tools to call
- **Interrupt Model Decision**: Can only interrupt before tool execution
- **Multiple Models**: One agent = one model (use subagents for multiple)

## Gotchas

### 1. Agent Doesn't Stop (Infinite Loop)

Set `max_iterations` to prevent runaway agents:

#### Python

```python
agent = create_agent(model="gpt-4.1", tools=[search], max_iterations=10)
```

#### TypeScript

```typescript
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool], maxIterations: 10 });
```

### 2. Tool Not Being Called

Use clear, specific tool descriptions. Vague descriptions like "Does stuff" won't help the model decide when to use the tool.

#### Python

```python
# ❌ Problem: Vague tool description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""  # Too vague!
    return "result"

# ✅ Solution: Clear, specific descriptions
@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data that wasn't in your training.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```

#### TypeScript

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

Add a checkpointer and use `thread_id` in config. Without a checkpointer, each invoke is isolated.

#### Python

```python
# ❌ Problem: No checkpointer
agent = create_agent(model="gpt-4.1", tools=[search])

# Each invoke is isolated - no memory
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember "Bob"

# ✅ Solution: Add checkpointer and thread_id
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Bob"
```

#### TypeScript

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

Access results correctly:

#### Python

```python
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result["messages"])  # List of all messages - correct
# print(result.content)    # KeyError! - wrong
```

#### TypeScript

```typescript
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.messages);  // Array of all messages - correct
// console.log(result.content); // undefined! - wrong
```

### 5. Tool Results Must Be Serializable

Return strings or JSON-serializable data from tools, not objects like `datetime` or custom classes.

#### Python

```python
from datetime import datetime

# ❌ Problem: Returning non-serializable objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime objects need special handling

# ✅ Solution: Return serializable data
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()  # String is serializable
```

#### TypeScript

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

- `"values"` - Full state after each step
- `"updates"` - Only what changed in each step
- `"messages"` - LLM token stream

### 7. Async Tools Must Be Awaited Properly (Python)

```python
from langchain.tools import tool

# ✅ Async tool properly defined
@tool
async def async_search(query: str) -> str:
    """Async search tool."""
    # Use await for async operations
    result = await some_async_api_call(query)
    return result

# Agent handles both sync and async tools
agent = create_agent(
    model="gpt-4.1",
    tools=[sync_tool, async_search],
)

# Use ainvoke for async execution
result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Search something"}]
})
```

## Links to Documentation

- Python: [Agents Overview](https://docs.langchain.com/oss/python/langchain/agents) | [Tool Calling](https://docs.langchain.com/oss/python/langchain/tools) | [Streaming](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- TypeScript: [Agents Overview](https://docs.langchain.com/oss/javascript/langchain/agents) | [Tool Calling](https://docs.langchain.com/oss/javascript/langchain/tools) | [Streaming](https://docs.langchain.com/oss/javascript/langchain/streaming/overview)
