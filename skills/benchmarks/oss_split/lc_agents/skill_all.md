---
name: LangChain Agents
description: "[LangChain] Create and use LangChain agents with create_agent - includes agent loops, ReAct pattern, tool execution, and state management"
---

<oneliner>
Agents combine language models with tools to create systems that can reason about tasks, decide which tools to use, and iteratively work towards solutions.
</oneliner>

<overview>
The `create_agent()`/`createAgent()` function provides a production-ready agent implementation built on LangGraph.

Key Concepts:
- **Agent Loop**: The model decides, calls tools, observes results, repeats until done
- **ReAct Pattern**: Reasoning and Acting - the agent reasons about what to do, then acts by calling tools
- **Graph-based Runtime**: Agents run on a LangGraph graph with nodes (model, tools, middleware) and edges
</overview>

<when-to-use>

| Scenario | Use Agent? | Why |
|----------|-----------|-----|
| Need to call external APIs/databases | Yes | Agents can dynamically choose which tools to call |
| Multi-step task with decision points | Yes | Agent loop handles iterative reasoning |
| Simple prompt-response | No | Use a chat model directly |
| Predetermined workflow | No | Use LangGraph workflow instead |
| Need tool calling without iteration | Maybe | Consider using model.bind_tools() directly |

</when-to-use>

<choosing-agent-configuration>

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `create_agent(model, tools)` | Search, calculator, weather |
| Custom system instructions | Add `system_prompt` | Domain-specific behavior |
| Human approval for sensitive operations | Add human-in-the-loop middleware | Database writes, emails |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |
| Structured output format | Add `response_format` | Extract contact info, parse forms |

</choosing-agent-configuration>

<tool-strategy>

| Tool Type | When to Use | Example |
|-----------|-------------|---------|
| Static tools | Tools don't change during execution | Search, weather, calculator |
| Dynamic tools | Tools depend on runtime state | User-specific APIs |
| Built-in tools | Need common functionality | File system, code execution |
| Custom tools | Domain-specific operations | Your business logic |

</tool-strategy>

<ex-basic>
<python>
Basic agent with search and weather tools:

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

</python>

<typescript>
Basic agent with search and weather tools:

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

</typescript>
</ex-basic>

<ex-system-prompt>
<python>
Agent with custom system prompt:

```python
agent = create_agent(
    model="gpt-4.1",
    tools=[search, calculator],
    system_prompt="""You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.""",
)
```

</python>

<typescript>
Agent with custom system prompt:

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
  systemPrompt: `You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.`,
});
```

</typescript>
</ex-system-prompt>

<ex-loop-flow>
The agent runs in a loop:
1. Model receives user message
2. Model decides to call a tool (or finish)
3. Tool executes and returns result
4. Result goes back to model
5. Repeat until model decides to finish

<python>
Agent loop handles multi-step tasks:

```python
agent = create_agent(model="gpt-4.1", tools=[search, get_weather])

# This single invoke() handles the entire loop
result = agent.invoke({
    "messages": [{"role": "user", "content": "Search for the capital of France, then get its weather"}]
})
# Agent automatically calls search → gets "Paris" → calls weather → responds
```

</python>

<typescript>
Agent loop handles multi-step tasks:

```typescript
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool, weatherTool] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for the capital of France, then get its weather" }],
});
```

</typescript>
</ex-loop-flow>

<ex-streaming>
<python>
Stream agent steps and tokens:

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

</python>

<typescript>
Stream agent steps and tokens:

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

</typescript>
</ex-streaming>

<ex-persistence>
<python>
Persist state across conversations:

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

</python>

<typescript>
Persist state across conversations:

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

</typescript>
</ex-persistence>

<ex-dynamic-tools>
<python>
Tools that depend on runtime state:

```python
def get_tools(state):
    """Tools can depend on current state."""
    user_id = state.get("config", {}).get("configurable", {}).get("user_id")
    return [get_user_specific_tool(user_id), common_tool]

agent = create_agent(model="gpt-4.1", tools=get_tools)  # Pass function instead of list
```

</python>

<typescript>
Tools that depend on runtime state:

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: (state) => {
    const userId = state.config?.configurable?.user_id;
    return [getUserSpecificTool(userId), commonTool];
  },
});
```

</typescript>
</ex-dynamic-tools>

<ex-tool-schema>
<python>
Tool with typed parameters:

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

</python>

<typescript>
Tool with typed parameters:

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

</typescript>
</ex-tool-schema>

<ex-parallel>
<python>
Parallel tool calls in one step:

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

</python>

<typescript>
Parallel tool calls in one step:

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

</typescript>
</ex-parallel>

<ex-error-handling>
<python>
Custom error handling middleware:

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

</python>

<typescript>
Custom error handling middleware:

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

</typescript>
</ex-error-handling>

<boundaries>
What Agents CAN Configure:
- **Model**: Any chat model (OpenAI, Anthropic, Google, etc.)
- **Tools**: Custom tools, built-in tools, dynamic tools
- **System Prompt**: Instructions for agent behavior
- **Middleware**: Human-in-the-loop, error handling, logging
- **Checkpointer**: Memory/persistence across conversations
- **Response Format**: Structured output schemas
- **Max Iterations**: Prevent infinite loops

What Agents CANNOT Configure:
- **Direct Graph Structure**: Use LangGraph directly for custom flows
- **Tool Execution Order**: Model decides which tools to call
- **Interrupt Model Decision**: Can only interrupt before tool execution
- **Multiple Models**: One agent = one model (use subagents for multiple)
</boundaries>

<fix-infinite-loop>
<python>
Limit iterations to prevent runaway agents:

```python
agent = create_agent(model="gpt-4.1", tools=[search], max_iterations=10)
```
</python>
<typescript>
Limit iterations to prevent runaway agents:

```typescript
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool], maxIterations: 10 });
```
</typescript>
</fix-infinite-loop>

<fix-tool-not-called>
<python>
Vague vs clear tool descriptions:

```python
# Bad: Vague tool description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""  # Too vague!
    return "result"

# Good: Clear, specific descriptions
@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data that wasn't in your training.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```
</python>
<typescript>
Vague vs clear tool descriptions:

```typescript
// Bad: Vague tool description
const badTool = tool(
  async ({ input }: { input: string }) => "result",
  {
    name: "tool",
    description: "Does stuff", // Too vague!
    schema: z.object({ input: z.string() }),
  }
);

// Good: Clear, specific descriptions
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
</typescript>
</fix-tool-not-called>

<fix-state-not-persisting>
<python>
Add checkpointer for conversation memory:

```python
# Problem: No checkpointer
agent = create_agent(model="gpt-4.1", tools=[search])

# Each invoke is isolated - no memory
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember "Bob"

# Solution: Add checkpointer and thread_id
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
</python>
<typescript>
Add checkpointer for conversation memory:

```typescript
// Problem: No checkpointer
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Each invoke is isolated - no memory
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember "Bob"

// Solution: Add checkpointer and thread_id
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
</typescript>
</fix-state-not-persisting>

<fix-messages-vs-state>
<python>
Access result messages correctly:

```python
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result["messages"])  # List of all messages - correct
# print(result.content)    # KeyError! - wrong
```
</python>
<typescript>
Access result messages correctly:

```typescript
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.messages);  // Array of all messages - correct
// console.log(result.content); // undefined! - wrong
```
</typescript>
</fix-messages-vs-state>

<fix-serializable-results>
<python>
Return JSON-serializable data from tools:

```python
from datetime import datetime

# Problem: Returning non-serializable objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime objects need special handling

# Solution: Return serializable data
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()  # String is serializable
```
</python>
<typescript>
Return JSON-serializable data from tools:

```typescript
// Problem: Returning non-serializable objects
const badTool = tool(
  async () => {
    return new Date(); // Date objects aren't JSON-serializable by default
  },
  { name: "get_time", description: "Get current time" }
);

// Solution: Return serializable data
const goodTool = tool(
  async () => {
    return new Date().toISOString(); // String is serializable
  },
  { name: "get_time", description: "Get current time" }
);
```
</typescript>
</fix-serializable-results>

<streaming-modes>
- `"values"` - Full state after each step
- `"updates"` - Only what changed in each step
- `"messages"` - LLM token stream
</streaming-modes>

<fix-async-tools>
<python>
Define and use async tools:

```python
from langchain.tools import tool

# Async tool properly defined
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
</python>
</fix-async-tools>

<links>
- Python: [Agents Overview](https://docs.langchain.com/oss/python/langchain/agents) | [Tool Calling](https://docs.langchain.com/oss/python/langchain/tools) | [Streaming](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- TypeScript: [Agents Overview](https://docs.langchain.com/oss/javascript/langchain/agents) | [Tool Calling](https://docs.langchain.com/oss/javascript/langchain/tools) | [Streaming](https://docs.langchain.com/oss/javascript/langchain/streaming/overview)
</links>
