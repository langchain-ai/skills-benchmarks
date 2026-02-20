---
name: langchain-fundamentals
description: Create LangChain agents with create_agent, define tools, and use middleware for human-in-the-loop and error handling
---

<oneliner>
Build production agents using `create_agent()`, the `@tool` decorator, and middleware patterns.
</oneliner>

<quick_start>
**Modern LangChain Agent Pattern:**

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    return f"Results for: {query}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",  # or "openai:gpt-4.1"
    tools=[search],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({"messages": [("user", "Search for LangChain docs")]})
```

**Key Imports:**
- `from langchain.agents import create_agent` - Agent factory
- `from langchain_core.tools import tool` - Tool decorator
- `from langchain.agents import human_in_the_loop_middleware` - Human approval
</quick_start>

<create_agent>
## Creating Agents with create_agent

`create_agent()` is the recommended way to build agents. It handles the agent loop, tool execution, and state management.

### Basic Agent

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72F"

@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    return f"Search results for: {query}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather, search],
    system_prompt="You are a helpful assistant that can search and check weather."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Paris?"}]
})
print(result["messages"][-1].content)
```

### Agent with Persistence

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    checkpointer=checkpointer,
)

# Conversation maintains state across invocations
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)
result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Alice"
```

### Agent Configuration Options

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `model` | LLM to use | `"anthropic:claude-sonnet-4-5"` or model instance |
| `tools` | List of tools | `[search, calculator]` |
| `system_prompt` | Agent instructions | `"You are a helpful assistant"` |
| `checkpointer` | State persistence | `MemorySaver()` |
| `middleware` | Processing hooks | `[human_in_the_loop_middleware]` |
| `max_iterations` | Loop limit | `10` |
| `response_format` | Structured output | Pydantic model |
</create_agent>

<tools>
## Defining Tools with @tool

Tools are functions that agents can call. Use the `@tool` decorator to create them.

### Basic Tool

```python
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: Math expression like "2 + 2" or "10 * 5"
    """
    allowed = set('0123456789+-*/(). ')
    if not all(c in allowed for c in expression):
        return "Error: Invalid characters in expression"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"
```

### Tool with Complex Parameters

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Literal, Optional

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Max results")
    category: Optional[Literal["news", "docs", "code"]] = None

@tool(args_schema=SearchParams)
def advanced_search(query: str, limit: int = 10, category: str = None) -> str:
    """Search with filters.

    Args:
        query: Search query
        limit: Maximum results
        category: Filter by category
    """
    return f"Found {limit} results for '{query}' in {category or 'all'}"
```

### Async Tool

```python
from langchain_core.tools import tool
import aiohttp

@tool
async def fetch_url(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### Tool Best Practices

**Good tool definition:**
```python
@tool
def search_customers(query: str) -> str:
    """Search customer database by name, email, or ID.

    Returns customer records with contact information.
    Use this when user asks about customer data.

    Args:
        query: Customer name, email, or ID to search for
    """
    return search_database(query)
```

**Bad tool definition:**
```python
@tool
def bad_tool(data: str) -> str:
    """Does something."""  # Too vague!
    return "result"
```
</tools>

<middleware>
## Middleware for Agent Control

Middleware intercepts the agent loop to add human approval, error handling, logging, etc.

### Human-in-the-Loop Middleware

Require human approval before executing sensitive tools:

```python
from langchain.agents import create_agent, human_in_the_loop_middleware

@tool
def delete_record(record_id: str) -> str:
    """Delete a database record permanently.

    Args:
        record_id: ID of record to delete
    """
    db.delete(record_id)
    return f"Deleted record {record_id}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[delete_record, search],
    middleware=[
        human_in_the_loop_middleware(
            tools_requiring_approval=["delete_record"]
        )
    ],
)

# Agent will pause and ask for approval before calling delete_record
```

### Error Handling Middleware

Catch and handle tool errors gracefully:

```python
from langchain.agents import create_agent, wrap_tool_call

@wrap_tool_call
async def error_handler(tool_call, handler):
    try:
        return await handler(tool_call)
    except Exception as error:
        return {
            **tool_call,
            "content": f"Tool error: {str(error)}. Please try a different approach.",
        }

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[risky_tool],
    middleware=[error_handler],
)
```

### Logging Middleware

Log all tool calls for debugging:

```python
from langchain.agents import wrap_tool_call

@wrap_tool_call
async def logging_middleware(tool_call, handler):
    print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")
    result = await handler(tool_call)
    print(f"Tool result: {result['content'][:100]}...")
    return result
```
</middleware>

<model_config>
## Model Configuration

### Model String Format

`create_agent` accepts model strings in `provider:model` format:

```python
# Anthropic
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[...])

# OpenAI
agent = create_agent(model="openai:gpt-4.1", tools=[...])

# AWS Bedrock
agent = create_agent(model="bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0", tools=[...])
```

### Using Model Instances

For more control, pass a model instance:

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Anthropic with custom settings
model = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0,
    max_tokens=4096,
)

# OpenAI with custom settings
model = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7,
)

agent = create_agent(model=model, tools=[...])
```

### Using init_chat_model

For dynamic provider selection:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="claude-sonnet-4-5",
    model_provider="anthropic",
    temperature=0,
)

agent = create_agent(model=model, tools=[...])
```
</model_config>

<streaming>
## Streaming Agent Output

### Stream Modes

```python
# Stream full state after each step
for mode, chunk in agent.stream(input, stream_mode=["values"]):
    print(chunk["messages"][-1])

# Stream only changes
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk)

# Stream LLM tokens
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    if token.content:
        print(token.content, end="", flush=True)
```

### Async Streaming

```python
async for mode, chunk in agent.astream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    stream_mode=["messages"],
):
    token, metadata = chunk
    if token.content:
        print(token.content, end="", flush=True)
```
</streaming>

<fix-missing-tool-description>
```python
# WRONG: Vague or missing description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""
    return "result"

# CORRECT: Clear, specific description with Args
@tool
def search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data or facts.

    Args:
        query: The search query (2-10 words recommended)
    """
    return web_search(query)
```
</fix-missing-tool-description>

<fix-no-checkpointer>
```python
# WRONG: No persistence - agent forgets between calls
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search])
agent.invoke({"messages": [{"role": "user", "content": "I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember!

# CORRECT: Add checkpointer and thread_id
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [{"role": "user", "content": "I'm Bob"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Bob"
```
</fix-no-checkpointer>

<fix-infinite-loop>
```python
# WRONG: No iteration limit - could loop forever
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search])
result = agent.invoke({
    "messages": [{"role": "user", "content": "Keep searching until you find everything"}]
})

# CORRECT: Set max_iterations
agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    max_iterations=10,  # Stop after 10 tool calls
)
```
</fix-infinite-loop>

<fix-non-serializable-return>
```python
from datetime import datetime

# WRONG: Returning non-JSON-serializable objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime not serializable!

# CORRECT: Return strings or JSON-serializable data
@tool
def get_time() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat()
```
</fix-non-serializable-return>

<fix-accessing-result-wrong>
```python
# WRONG: Trying to access result.content directly
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result.content)  # AttributeError!

# CORRECT: Access messages from result dict
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result["messages"][-1].content)  # Last message content
```
</fix-accessing-result-wrong>

<related_skills>
- **langgraph-fundamentals**: For custom graph-based agents with StateGraph
- **langgraph-persistence**: For advanced persistence patterns with checkpointers
- **langchain-output**: For structured output with Pydantic models
- **langchain-rag**: For RAG pipelines with vector stores
</related_skills>
