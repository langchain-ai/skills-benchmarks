---
name: LangChain Agents & Tools
description: "INVOKE THIS SKILL when building ANY LangChain/LangGraph agent with tools. Covers create_react_agent, @tool decorator, Pydantic schemas for tools, bind_tools(), and tool message handling. CRITICAL: Fixes for missing tool docstrings/types, tool_call_id mismatches, and not checking for tool_calls in responses."
---

<overview>
Agents combine language models with tools to create systems that can reason, act, and iterate.

**Key Components:**
- **@tool / tool()**: Create tools from functions
- **bind_tools()**: Attach tools to a model
- **Tool Calls**: Model requests in AIMessage.tool_calls
- **ToolMessage**: Results passed back to model
- **create_agent()**: Production-ready agent built on LangGraph
</overview>

<agent-configuration-selection>

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `create_agent(model, tools)` | Search, calculator |
| Custom system instructions | Add `system_prompt` | Domain-specific behavior |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |

</agent-configuration-selection>

<tool-choice-strategies>

| Strategy | When to Use |
|----------|-------------|
| `"auto"` (default) | Model decides if/which tool |
| `"any"` | Force model to use at least one tool |
| `"tool_name"` | Force specific tool |

</tool-choice-strategies>

---

## Tool Definition

<ex-basic-tool>
<python>
Define a calculator tool using the @tool decorator with typed parameters.
```python
from langchain.tools import tool
from typing import Literal

@tool
def calculator(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> float:
    """Perform mathematical calculations.

    Args:
        operation: The mathematical operation to perform
        a: First number
        b: Second number
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return ops[operation]
```
</python>
<typescript>
Define a calculator tool using the tool() function with Zod schema validation.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const calculator = tool(
  async ({ operation, a, b }) => {
    const ops = { add: a + b, subtract: a - b, multiply: a * b, divide: a / b };
    return ops[operation];
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```
</typescript>
</ex-basic-tool>

<ex-tool-with-schema>
<python>
Define a tool with explicit Pydantic schema for argument validation.
```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Max results")

@tool(args_schema=SearchParams)
def search_database(query: str, limit: int = 10) -> str:
    """Search the database for records."""
    return f"Found {limit} results for: {query}"
```
</python>
<typescript>
Define a tool with Zod schema for argument validation with default values.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchDatabase = tool(
  async ({ query, limit }) => `Found ${limit} results for: ${query}`,
  {
    name: "search_database",
    description: "Search the database for records",
    schema: z.object({
      query: z.string().describe("Search query"),
      limit: z.number().default(10).describe("Max results"),
    }),
  }
);
```
</typescript>
</ex-tool-with-schema>

<ex-async-tool>
<python>
Define an async tool for non-blocking I/O operations like HTTP requests.
```python
from langchain.tools import tool
import aiohttp

@tool
async def fetch_weather(location: str) -> str:
    """Get current weather conditions for a location.

    Args:
        location: City name or ZIP code
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.weather.com/v1/{location}") as response:
            data = await response.json()
            return f"Temperature: {data['temp']}F, Conditions: {data['conditions']}"
```
</python>
</ex-async-tool>

---

## Agent Creation

<ex-basic-agent-with-tools>
<python>
Create a basic agent with a search tool and invoke it with a user message.
```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web."""
    return f"Results for: {query}"

agent = create_agent(
    model="gpt-4",
    tools=[search],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Search for AI news"}]
})
print(result["messages"][-1].content)
```
</python>
<typescript>
Create a basic React agent with a search tool and invoke it with a user message.
```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => `Results for: ${query}`,
  { name: "search", description: "Search for information", schema: z.object({ query: z.string() }) }
);

const model = new ChatOpenAI({ model: "gpt-4" });
const agent = createReactAgent({ llm: model, tools: [search] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for AI news" }]
});
console.log(result.messages.at(-1).content);
```
</typescript>
</ex-basic-agent-with-tools>

<ex-agent-with-persistence>
<python>
Create an agent with MemorySaver checkpointer for conversation persistence across invokes.
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4",
    tools=[search],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)

result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Response: "Your name is Alice"
```
</python>
<typescript>
Create a React agent with MemorySaver checkpointer for conversation persistence across invokes.
```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";

const agent = createReactAgent({
  llm: model,
  tools: [search],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);

const result = await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Response: "Your name is Alice"
```
</typescript>
</ex-agent-with-persistence>

---

## Tool Calling (Manual)

<ex-basic-tool-calling>
<python>
Bind a tool to a model and inspect the tool_calls returned by the model.
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}: Sunny, 72F"

model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke("What's the weather in SF?")
print(response.tool_calls)
# [{'name': 'get_weather', 'args': {'location': 'San Francisco'}, 'id': 'call_abc123'}]
```
</python>
<typescript>
Bind a tool to a model and inspect the tool_calls returned by the model.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny, 72F`,
  { name: "get_weather", description: "Get weather", schema: z.object({ location: z.string() }) }
);

const model = new ChatOpenAI({ model: "gpt-4" });
const modelWithTools = model.bindTools([getWeather]);

const response = await modelWithTools.invoke("What's the weather in SF?");
console.log(response.tool_calls);
// [{ name: 'get_weather', args: { location: 'San Francisco' }, id: 'call_abc123' }]
```
</typescript>
</ex-basic-tool-calling>

<ex-executing-tool-calls>
<python>
Execute tool calls from the model response and pass results back for final answer.
```python
from langchain.schema.messages import ToolMessage

# Step 1: Model decides to call tool
messages = [{"role": "user", "content": "What's the weather in NYC?"}]
response1 = model_with_tools.invoke(messages)

# Step 2: Execute the tool
tool_results = []
for tool_call in response1.tool_calls:
    result = get_weather.invoke(tool_call)
    tool_results.append(result)

# Step 3: Pass results back to model
messages.append(response1)
messages.extend(tool_results)

response2 = model_with_tools.invoke(messages)
print(response2.content)
```
</python>
<typescript>
Execute tool calls from the model response and pass results back for final answer.
```typescript
import { ToolMessage } from "@langchain/core/messages";

// Step 1: Model decides to call tool
const messages = [{ role: "user", content: "What's the weather in NYC?" }];
const response1 = await modelWithTools.invoke(messages);

// Step 2: Execute the tool
const toolResults = [];
for (const toolCall of response1.tool_calls ?? []) {
  const result = await getWeather.invoke(toolCall.args);
  toolResults.push(new ToolMessage({ content: result, tool_call_id: toolCall.id }));
}

// Step 3: Pass results back to model
messages.push(response1);
messages.push(...toolResults);

const response2 = await modelWithTools.invoke(messages);
console.log(response2.content);
```
</typescript>
</ex-executing-tool-calls>

<ex-parallel-tool-calling>
<python>
Models may return multiple tool_calls at once - iterate over all of them.
```python
response = model_with_tools.invoke("Get weather for NYC and news about AI")

# Model may call both tools in parallel
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'NYC'}, 'id': 'call_1'},
#   {'name': 'get_news', 'args': {'topic': 'AI'}, 'id': 'call_2'}
# ]

# Execute ALL tool calls, not just the first one
for tool_call in response.tool_calls:
    result = tools_by_name[tool_call["name"]].invoke(tool_call)
```
</python>
<typescript>
Models may return multiple tool_calls at once - iterate over all of them.
```typescript
const response = await modelWithTools.invoke("Get weather for NYC and news about AI");

// Model may call both tools in parallel
console.log(response.tool_calls);
// [
//   { name: 'get_weather', args: { location: 'NYC' }, id: 'call_1' },
//   { name: 'get_news', args: { topic: 'AI' }, id: 'call_2' }
// ]

// Execute ALL tool calls, not just the first one
for (const toolCall of response.tool_calls ?? []) {
  const result = await toolsByName[toolCall.name].invoke(toolCall.args);
}
```
</typescript>
</ex-parallel-tool-calling>

<ex-tool-choice-force-tool>
<python>
Force the model to use a specific tool or require at least one tool call.
```python
# Force model to use this specific tool
model_with_tools = model.bind_tools(
    [extract_info],
    tool_choice="extract_info"  # Must use this tool
)

# Or force any tool (model picks which)
model_with_tools = model.bind_tools(
    [tool1, tool2, tool3],
    tool_choice="any"
)
```
</python>
</ex-tool-choice-force-tool>

<boundaries>
### What You CAN Configure

- Model: Any chat model (OpenAI, Anthropic, etc.)
- Tools: Custom tools, built-in tools
- Checkpointer: Memory/persistence
- Tool choice strategy: auto, any, specific tool

### What You CANNOT Configure

- Tool execution order: Model decides
- Force model reasoning: Can't control how model decides
</boundaries>

<fix-tool-description>
<python>
Use clear, specific descriptions so model knows when to use the tool.
```python
# WRONG: Vague
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""
    return "result"

# CORRECT
@tool
def web_search(query: str) -> str:
    """Search the web for current information.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```
</python>
<typescript>
Use clear, specific descriptions so model knows when to use the tool.
```typescript
// WRONG: Vague
const badTool = tool(async ({ data }) => "result", { name: "tool", description: "Does something", schema: z.object({ data: z.string() }) });

// CORRECT
const goodTool = tool(async ({ query }) => "result", {
  name: "web_search",
  description: "Search the web for current information",
  schema: z.object({ query: z.string().describe("Search query (2-10 words)") })
});
```
</typescript>
</fix-tool-description>

<fix-missing-docstrings>
<python>
Tools must have docstrings so model knows when to use them.
```python
# WRONG: No docstring
@tool
def bad_tool(input: str) -> str:
    return "result"

# CORRECT
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Args:
        input: The data to process
    """
    return "result"
```
</python>
</fix-missing-docstrings>

<fix-non-serializable-return>
<python>
Tool return values must be JSON-serializable strings.
```python
# WRONG: datetime not JSON-serializable
@tool
def bad_get_time() -> datetime:
    return datetime.now()

# CORRECT
@tool
def good_get_time() -> str:
    return datetime.now().isoformat()
```
</python>
</fix-non-serializable-return>

<fix-forgetting-to-pass-tool-results-back>
<python>
Always pass tool results back to the model.
```python
# WRONG: Missing results
response1 = model_with_tools.invoke(messages)
tool_result = tool.invoke(response1.tool_calls[0])

# CORRECT
messages.append(response1)
messages.append(tool_result)
response2 = model_with_tools.invoke(messages)
```
</python>
<typescript>
Always pass tool results back to the model.
```typescript
// WRONG: Missing results
const response1 = await modelWithTools.invoke(messages);
const toolResult = await tool.invoke(response1.tool_calls[0].args);

// CORRECT
messages.push(response1);
messages.push(new ToolMessage({ content: toolResult, tool_call_id: response1.tool_calls[0].id }));
const response2 = await modelWithTools.invoke(messages);
```
</typescript>
</fix-forgetting-to-pass-tool-results-back>

<fix-tool-call-id-mismatch>
<python>
ToolMessage tool_call_id must match the original request.
```python
# WRONG
tool_message = ToolMessage(content="Sunny", tool_call_id="wrong_id", name="get_weather")

# CORRECT: Use ID from tool call (or let tool.invoke handle it)
tool_message = ToolMessage(content="Sunny", tool_call_id=response.tool_calls[0]["id"], name="get_weather")
tool_message = get_weather.invoke(response.tool_calls[0])  # Automatic
```
</python>
<typescript>
ToolMessage tool_call_id must match the original request.
```typescript
// WRONG
new ToolMessage({ content: "Sunny", tool_call_id: "wrong_id", name: "get_weather" });

// CORRECT: Use ID from tool call (or let tool.invoke handle it)
new ToolMessage({ content: "Sunny", tool_call_id: response.tool_calls[0].id, name: "get_weather" });
await getWeather.invoke(response.tool_calls[0]);  // Automatic
```
</typescript>
</fix-tool-call-id-mismatch>

<fix-not-checking-for-tool-calls>
<python>
Check if tool_calls exist before executing.
```python
# WRONG: Assuming model always calls tools
tool.invoke(response.tool_calls[0])  # Error if no tool calls!

# CORRECT
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool.invoke(tool_call)
else:
    print(response.content)
```
</python>
<typescript>
Check if tool_calls exist before executing.
```typescript
// WRONG: Assuming model always calls tools
await tool.invoke(response.tool_calls[0].args);  // Error!

// CORRECT
if (response.tool_calls?.length) {
  for (const toolCall of response.tool_calls) await tool.invoke(toolCall.args);
} else {
  console.log(response.content);
}
```
</typescript>
</fix-not-checking-for-tool-calls>

<fix-binding-tools-multiple-times>
<python>
Bind all tools at once - chaining bind_tools overwrites previous.
```python
# WRONG: Only has tool2
with_tool1 = model.bind_tools([tool1])
with_tool2 = with_tool1.bind_tools([tool2])

# CORRECT
with_both_tools = model.bind_tools([tool1, tool2])
```
</python>
<typescript>
Bind all tools at once - chaining bindTools overwrites previous.
```typescript
// WRONG: Only has tool2
const withTool2 = model.bindTools([tool1]).bindTools([tool2]);

// CORRECT
const withBothTools = model.bindTools([tool1, tool2]);
```
</typescript>
</fix-binding-tools-multiple-times>

<fix-state-persistence>
<python>
Add checkpointer and thread_id to enable conversation memory.
```python
# WRONG: No checkpointer - each invoke is isolated
agent = create_agent(model="gpt-4", tools=[search])

# CORRECT
agent = create_agent(model="gpt-4", tools=[search], checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [...]}, config=config)
```
</python>
<typescript>
Add checkpointer and thread_id to enable conversation memory.
```typescript
// WRONG: No checkpointer - each invoke is isolated
const agent = createReactAgent({ llm: model, tools: [search] });

// CORRECT
const agent = createReactAgent({ llm: model, tools: [search], checkpointer: new MemorySaver() });
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [...] }, config);
```
</typescript>
</fix-state-persistence>

<fix-infinite-loop>
<python>
Set max_iterations to prevent agents from looping indefinitely.
```python
# PROBLEM: No stopping condition
agent = create_agent(model="gpt-4.1", tools=[search])

# SOLUTION
agent = create_agent(model="gpt-4.1", tools=[search], max_iterations=10)
```
</python>
</fix-infinite-loop>
