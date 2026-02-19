---
name: LangChain Agents (Python)
description: "[LangChain] Create and use LangChain agents with create_agent - includes agent loops, ReAct pattern, tool execution, and state management"
---

<overview>
Agents combine language models with tools to create systems that can reason about tasks, decide which tools to use, and iteratively work towards solutions. The `create_agent()` function provides a production-ready agent implementation built on LangGraph.

**Key Concepts:**
- **Agent Loop**: The model decides → calls tools → observes results → repeats until done
- **ReAct Pattern**: Reasoning and Acting - the agent reasons about what to do, then acts by calling tools
- **Graph-based Runtime**: Agents run on a LangGraph graph with nodes (model, tools, middleware) and edges
</overview>

<when-to-use-agents>

| Scenario | Use Agent? | Why |
|----------|-----------|-----|
| Need to call external APIs/databases | Yes | Agents can dynamically choose which tools to call |
| Multi-step task with decision points | Yes | Agent loop handles iterative reasoning |
| Simple prompt-response | No | Use a chat model directly |
| Predetermined workflow | No | Use LangGraph workflow instead |
| Need tool calling without iteration | Partial Maybe | Consider using model.bind_tools() directly |

</when-to-use-agents>

<agent-configuration-selection>

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `create_agent(model, tools)` | Search, calculator, weather |
| Custom system instructions | Add `system_prompt` | Domain-specific behavior |
| Human approval for sensitive operations | Add `human_in_the_loop_middleware` | Database writes, emails |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |
| Structured output format | Add `response_format` | Extract contact info, parse forms |

</agent-configuration-selection>

<tool-strategy>

| Tool Type | When to Use | Example |
|-----------|-------------|---------|
| Static tools | Tools don't change during execution | Search, weather, calculator |
| Dynamic tools | Tools depend on runtime state | User-specific APIs |
| Built-in tools | Need common functionality | File system, code execution |
| Custom tools | Domain-specific operations | Your business logic |

</tool-strategy>

<ex-basic-agent-with-tools>
```python
from langchain.agents import create_agent
from langchain.tools import tool

# Define tools using @tool decorator
@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    # Your search implementation
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72°F"

# Create agent
agent = create_agent(
    model="gpt-4.1",
    tools=[search, get_weather],
)

# Invoke agent
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ]
})

print(result["messages"][-1].content)
```
</ex-basic-agent-with-tools>

<ex-agent-with-system-prompt>
```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search, calculator],
    system_prompt="""You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.""",
)
```
</ex-agent-with-system-prompt>

<ex-agent-loop-execution>
```python
# The agent runs in a loop:
# 1. Model receives user message
# 2. Model decides to call a tool (or finish)
# 3. Tool executes and returns result
# 4. Result goes back to model
# 5. Repeat until model decides to finish

agent = create_agent(
    model="gpt-4.1",
    tools=[search, get_weather],
)

# This single invoke() call handles the entire loop
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Search for the capital of France, then get its weather"
    }]
})

# Agent automatically:
# - Calls search tool for capital
# - Receives "Paris"
# - Calls weather tool for Paris
# - Receives weather data
# - Responds with final answer
```
</ex-agent-loop-execution>

<ex-streaming-agent>
```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
)

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
</ex-streaming-agent>

<ex-agent-with-persistence>
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    checkpointer=checkpointer,
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

<ex-parallel-tool-calls>
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
</ex-parallel-tool-calls>

<ex-dynamic-tools>
```python
from langchain.agents import create_agent

def get_tools(state):
    """Tools can depend on current state."""
    user_id = state.get("config", {}).get("configurable", {}).get("user_id")
    return [
        get_user_specific_tool(user_id),
        common_tool,
    ]

agent = create_agent(
    model="gpt-4.1",
    tools=get_tools,  # Pass function instead of list
)
```
</ex-dynamic-tools>

<ex-error-handling>
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
</ex-error-handling>

<ex-typed-tool>
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
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
```
</ex-typed-tool>

<boundaries>
### What Agents CAN Configure

* Model**: Any chat model (OpenAI, Anthropic, Google, etc.)
* Tools**: Custom tools, built-in tools, dynamic tools
* System Prompt**: Instructions for agent behavior
* Middleware**: Human-in-the-loop, error handling, logging
* Checkpointer**: Memory/persistence across conversations
* Response Format**: Structured output schemas (Pydantic, TypedDict, JSON Schema)
* Max Iterations**: Prevent infinite loops

### What Agents CANNOT Configure

* Direct Graph Structure**: Use LangGraph directly for custom flows
* Tool Execution Order**: Model decides which tools to call
* Interrupt Model Decision**: Can only interrupt before tool execution
* Multiple Models**: One agent = one model (use subagents for multiple)
</boundaries>

<fix-infinite-loop>
```python
# WRONG: Problem: No clear stopping condition
agent = create_agent(
    model="gpt-4.1",
    tools=[search],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Keep searching until perfect"}]
})

# CORRECT: Solution: Set max iterations
agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    max_iterations=10,  # Stop after 10 tool calls
)
```
</fix-infinite-loop>

<fix-tool-description>
```python
# WRONG: Problem: Vague tool description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""  # Too vague!
    return "result"

# CORRECT: Solution: Clear, specific descriptions
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

<fix-state-persistence>
```python
# WRONG: Problem: No checkpointer
agent = create_agent(
    model="gpt-4.1",
    tools=[search],
)

# Each invoke is isolated - no memory
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember "Bob"

# CORRECT: Solution: Add checkpointer and thread_id
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

<fix-messages-vs-state>
```python
# Agent state includes more than just messages
result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello"}]
})

# CORRECT: Access full conversation history
print(result["messages"])  # List of all messages

# CORRECT: Access structured output (if configured)
print(result.get("structured_response"))

# WRONG: Don't try to access result.content directly
# print(result.content)  # KeyError!
```
</fix-messages-vs-state>

<fix-serializable-tool-results>
```python
from datetime import datetime

# WRONG: Problem: Returning non-serializable objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime objects need special handling

# CORRECT: Solution: Return serializable data
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()  # String is serializable
```
</fix-serializable-tool-results>

<fix-streaming-modes>
```python
# Different stream modes show different information

# "values" - Full state after each step
for mode, chunk in agent.stream(input, stream_mode=["values"]):
    print(chunk["messages"])  # All messages so far

# "updates" - Only what changed in each step
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk)  # Just the delta

# "messages" - LLM token stream
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content, end="", flush=True)
```
</fix-streaming-modes>

<fix-async-tools>
```python
from langchain.tools import tool

# CORRECT: Async tool properly defined
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
</fix-async-tools>

<links>
- [Agents Overview](https://docs.langchain.com/oss/python/langchain/agents)
- [create_agent API Reference](https://docs.langchain.com/oss/python/releases/langchain-v1)
- [LangGraph Concepts](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Tool Calling Guide](https://docs.langchain.com/oss/python/langchain/tools)
- [Streaming Guide](https://docs.langchain.com/oss/python/langchain/streaming/overview)
- [Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
</links>
