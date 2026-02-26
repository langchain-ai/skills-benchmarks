---
name: LangChain Agents & Tools (Python)
description: "INVOKE THIS SKILL when building ANY LangChain/LangGraph agent with tools. Covers create_react_agent, @tool decorator, Pydantic schemas, bind_tools(), and tool message handling. CRITICAL: Fixes for missing tool docstrings/types, tool_call_id mismatches, and not checking for tool_calls."
---

<overview>
Agents combine language models with tools to create systems that can reason, act, and iterate. The agent decides which tools to call, executes them, observes results, and repeats until done.

**Key Components:**
- **@tool**: Decorator to create tools from functions
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
| Human approval for sensitive ops | Add `HumanInTheLoopMiddleware` | DB writes, emails |

</agent-configuration-selection>

<tool-choice-strategies>

| Strategy | When to Use | Example |
|----------|-------------|---------|
| `"auto"` (default) | Model decides if/which tool | General purpose |
| `"any"` | Force model to use at least one tool | Extraction, classification |
| `"tool_name"` | Force specific tool | When you know which tool is needed |
| `"none"` | Prevent tool use | After tools are executed |

</tool-choice-strategies>

---

## Tool Definition

<ex-basic-tool>
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

    Use this when you need to compute numbers.

    Args:
        operation: The mathematical operation to perform
        a: First number
        b: Second number
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return ops[operation]
```
</ex-basic-tool>

<ex-tool-with-pydantic-schema>
```python
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

class SearchParams(BaseModel):
    query: str = Field(description="Search query (keywords or customer name)")
    limit: int = Field(default=10, description="Maximum number of results")

@tool(args_schema=SearchParams)
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching criteria."""
    return f"Found {limit} results for: {query}"
```
</ex-tool-with-pydantic-schema>

<ex-async-tool>
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
</ex-async-tool>

---

## Agent Creation

<ex-basic-agent-with-tools>
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

agent = create_agent(
    model="gpt-4.1",
    tools=[search, get_weather],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF?"}]
})
print(result["messages"][-1].content)
```
</ex-basic-agent-with-tools>

<ex-agent-with-persistence>
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    checkpointer=MemorySaver(),
)

# First conversation
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({
    "messages": [{"role": "user", "content": "My name is Alice"}]
}, config=config)

# Later conversation - agent remembers
result = agent.invoke({
    "messages": [{"role": "user", "content": "What's my name?"}]
}, config=config)
# Response: "Your name is Alice"
```
</ex-agent-with-persistence>

---

## Tool Calling (Manual)

<ex-basic-tool-calling>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

# Bind tool to model
model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke("What's the weather in San Francisco?")

# Check if model called a tool
print(response.tool_calls)
# [{'name': 'get_weather', 'args': {'location': 'San Francisco'}, 'id': 'call_abc123'}]
```
</ex-basic-tool-calling>

<ex-executing-tool-calls>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage

@tool
def get_weather(location: str) -> str:
    """Get weather."""
    return f"Weather in {location}: Sunny"

model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([get_weather])

# Step 1: Model decides to call tool
messages = [{"role": "user", "content": "What's the weather in NYC?"}]
response1 = model_with_tools.invoke(messages)

# Step 2: Execute the tool
tool_results = []
for tool_call in response1.tool_calls:
    result = get_weather.invoke(tool_call)
    tool_results.append(result)  # This is a ToolMessage

# Step 3: Pass results back to model
messages.append(response1)       # Add AI message with tool calls
messages.extend(tool_results)    # Add tool results

response2 = model_with_tools.invoke(messages)
print(response2.content)  # Final answer using tool results
```
</ex-executing-tool-calls>

<ex-tool-choice-force-tool>
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
</ex-tool-choice-force-tool>

<ex-parallel-tool-calling>
```python
@tool
def get_weather(location: str) -> str:
    """Get weather."""
    return f"Weather in {location}: Sunny"

@tool
def get_news(topic: str) -> str:
    """Get news."""
    return f"Latest news about {topic}"

model_with_tools = model.bind_tools([get_weather, get_news])

response = model_with_tools.invoke("Get weather for NYC and news about AI")

# Model may call both tools in parallel
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'NYC'}, 'id': 'call_1'},
#   {'name': 'get_news', 'args': {'topic': 'AI'}, 'id': 'call_2'}
# ]
```
</ex-parallel-tool-calling>

<boundaries>
### What You CAN Configure

- Model: Any chat model (OpenAI, Anthropic, Google, etc.)
- Tools: Custom tools, built-in tools, dynamic tools
- System Prompt: Instructions for agent behavior
- Checkpointer: Memory/persistence across conversations
- Tool choice strategy: auto, any, specific tool, none
- Max iterations: Prevent infinite loops

### What You CANNOT Configure

- Tool execution order: Model decides which tools to call
- Force model reasoning: Can't control how model decides
- Direct graph structure: Use LangGraph directly for custom flows
</boundaries>

<fix-tool-description>
```python
# WRONG: Vague tool description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""  # Too vague!
    return "result"

# CORRECT: Clear, specific descriptions
@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data that wasn't in your training.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```
</fix-tool-description>

<fix-missing-docstrings>
```python
# WRONG: No docstring - model won't know when to use
@tool
def bad_tool(input: str) -> str:
    return "result"  # No description!

# CORRECT: Always provide docstring
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Use this tool when you need to transform user input.

    Args:
        input: The data to process
    """
    return "result"
```
</fix-missing-docstrings>

<fix-non-serializable-return>
```python
from datetime import datetime

# WRONG: Returning complex objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime not JSON-serializable

# CORRECT: Return strings or JSON
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()
```
</fix-non-serializable-return>

<fix-forgetting-to-pass-tool-results-back>
```python
# WRONG: Not passing tool results back to model
response1 = model_with_tools.invoke(messages)
tool_result = tool.invoke(response1.tool_calls[0])
# Missing: passing result back to model!

# CORRECT: Always pass results back
messages.append(response1)      # AI message with tool calls
messages.append(tool_result)    # Tool result
response2 = model_with_tools.invoke(messages)
```
</fix-forgetting-to-pass-tool-results-back>

<fix-tool-call-id-mismatch>
```python
# WRONG: Wrong tool_call_id
response = model_with_tools.invoke("Get weather")
tool_message = ToolMessage(
    content="Sunny",
    tool_call_id="wrong_id",  # Doesn't match!
    name="get_weather",
)

# CORRECT: Use correct ID from tool call
tool_message = ToolMessage(
    content="Sunny",
    tool_call_id=response.tool_calls[0]["id"],  # Correct ID
    name="get_weather",
)

# OR use tool.invoke() which handles this automatically
tool_message = get_weather.invoke(response.tool_calls[0])
```
</fix-tool-call-id-mismatch>

<fix-not-checking-for-tool-calls>
```python
# WRONG: Assuming model always calls tools
response = model_with_tools.invoke("Hello")
tool.invoke(response.tool_calls[0])  # Error if no tool calls!

# CORRECT: Check if tool calls exist
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool.invoke(tool_call)
else:
    # Model responded without calling tools
    print(response.content)
```
</fix-not-checking-for-tool-calls>

<fix-binding-tools-multiple-times>
```python
# WRONG: Binding tools overwrites previous binding
model = ChatOpenAI(model="gpt-4.1")
with_tool1 = model.bind_tools([tool1])
with_tool2 = with_tool1.bind_tools([tool2])  # Only has tool2!

# CORRECT: Bind all tools at once
with_both_tools = model.bind_tools([tool1, tool2])
```
</fix-binding-tools-multiple-times>

<fix-state-persistence>
```python
# WRONG: No checkpointer - each invoke is isolated
agent = create_agent(model="gpt-4.1", tools=[search])

agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember "Bob"

# CORRECT: Add checkpointer and thread_id
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
</fix-state-persistence>

<fix-infinite-loop>
```python
# PROBLEM: No clear stopping condition
result = agent.invoke({"messages": [("user", "Keep searching until perfect")]})

# SOLUTION: Set recursion_limit in config
result = agent.invoke(
    {"messages": [("user", "Keep searching until perfect")]},
    config={"recursion_limit": 10},  # Stop after 10 steps
)
```
</fix-infinite-loop>
