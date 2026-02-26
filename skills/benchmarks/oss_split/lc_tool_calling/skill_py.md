---
name: LangChain Tool Calling (Python)
description: "[LangChain] How chat models call tools - includes bind_tools, tool choice strategies, parallel tool calling, and tool message handling"
---

<overview>
Tool calling allows chat models to request execution of external functions. Models decide which tools to call based on user input, and the results are passed back to the model for further reasoning. This is the foundation of agentic behavior.

**Key Concepts:**
- **bind_tools()**: Attach tools to a model
- **Tool Calls**: Model requests to execute tools (in AIMessage.tool_calls)
- **Tool Messages**: Results passed back to model (ToolMessage)
- **Tool Choice**: Control which tools the model can use
</overview>

<when-to-use-tool-calling>

| Scenario | Use Tool Calling? | Why |
|----------|------------------|-----|
| Need external data (API, database) | Yes | Model can't access external data directly |
| Multi-step reasoning with actions | Yes | Model decides next action based on results |
| Simple Q&A | No | No tools needed |
| Predetermined workflow | Partial Maybe | Consider if model needs to decide steps |

</when-to-use-tool-calling>

<tool-choice-strategies>

| Strategy | When to Use | Example |
|----------|-------------|---------|
| `"auto"` (default) | Model decides if/which tool to use | General purpose |
| `"any"` | Force model to use at least one tool | Extraction, classification |
| `"tool_name"` | Force specific tool | When you know which tool is needed |
| `"none"` | Prevent tool use | After tools are executed |

</tool-choice-strategies>

<handling-tool-calls>

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Manual execution | Outside of agents | Testing, custom workflows |
| Agent loop | Production use | create_agent handles automatically |
| Parallel execution | Multiple independent tools | Weather + news queries |

</handling-tool-calls>

<ex-basic-tool-calling>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# Define a tool
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72°F"

# Bind tool to model
model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([get_weather])

# Model will decide to call the tool
response = model_with_tools.invoke("What's the weather in San Francisco?")

# Check if model called a tool
print(response.tool_calls)
# [{
#   'name': 'get_weather',
#   'args': {'location': 'San Francisco'},
#   'id': 'call_abc123'
# }]
```
</ex-basic-tool-calling>

<ex-executing-tool-calls-manually>
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
messages.append(response1)  # Add AI message with tool calls
messages.extend(tool_results)  # Add tool results

response2 = model_with_tools.invoke(messages)
print(response2.content)  # Final answer using tool results
```
</ex-executing-tool-calls-manually>

<ex-tool-choice-force-tool-use>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str

@tool
def extract_info(name: str, email: str) -> dict:
    """Extract name and email.

    Args:
        name: Person's name
        email: Email address
    """
    return {"name": name, "email": email}

model = ChatOpenAI(model="gpt-4.1")

# Force model to use this specific tool
model_with_tools = model.bind_tools(
    [extract_info],
    tool_choice="extract_info"  # Must use this tool
)

response = model_with_tools.invoke("Contact: John Doe (john@example.com)")

# Model always calls extract_info
print(response.tool_calls[0]["args"])
# {'name': 'John Doe', 'email': 'john@example.com'}
```
</ex-tool-choice-force-tool-use>

<ex-tool-choice-force-any-tool>
```python
# Force model to use at least one tool (any of them)
model_with_tools = model.bind_tools(
    [tool1, tool2, tool3],
    tool_choice="any"
)

# Model must call at least one tool, can't respond with just text
response = model_with_tools.invoke("Process this data")
```
</ex-tool-choice-force-any-tool>

<ex-parallel-tool-calling>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather."""
    return f"Weather in {location}: Sunny"

@tool
def get_news(topic: str) -> str:
    """Get news."""
    return f"Latest news about {topic}"

model = ChatOpenAI(model="gpt-4.1")
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

<ex-tool-message-structure>
```python
from langchain_core.messages import ToolMessage

# Tool messages link back to the tool call that requested them
tool_message = ToolMessage(
    content="Weather in Paris: Sunny, 72°F",
    tool_call_id="call_abc123",  # Must match AIMessage tool_call id
    name="get_weather",  # Tool name
)

# Or created automatically by tool.invoke()
result = get_weather.invoke({
    "name": "get_weather",
    "args": {"location": "Paris"},
    "id": "call_abc123",
})
# result is a ToolMessage with proper structure
```
</ex-tool-message-structure>

<ex-handling-tool-errors>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage

@tool
def risky_tool(data: str = None) -> str:
    """A tool that might fail."""
    if not data:
        raise ValueError("Missing data")
    return "Success"

model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([risky_tool])

response = model_with_tools.invoke("Process this")

# Execute tools with error handling
tool_results = []
for tool_call in response.tool_calls:
    try:
        result = risky_tool.invoke(tool_call)
        tool_results.append(result)
    except Exception as error:
        # Return error as tool message
        tool_results.append(
            ToolMessage(
                content=f"Error: {str(error)}",
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        )
```
</ex-handling-tool-errors>

<ex-provider-specific-built-in-tools>
```python
from langchain_openai import ChatOpenAI

# OpenAI has built-in tools
model = ChatOpenAI(
    model="gpt-4.1",
    # Some models support built-in tools (check provider docs)
)

# Anthropic has built-in tools
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    # Provider-specific parameters
)
```
</ex-provider-specific-built-in-tools>

<ex-conditional-tool-binding>
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

def get_model_with_tools(user_role: str):
    tools = [public_tool]

    if user_role == "admin":
        tools.append(admin_tool)

    return model.bind_tools(tools)

# Different users get different tools
admin_model = get_model_with_tools("admin")
user_model = get_model_with_tools("user")
```
</ex-conditional-tool-binding>

<ex-tool-calling-in-conversation>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([search])

messages = [
    {"role": "user", "content": "Search for LangChain"},
]

# First call: model decides to use tool
response1 = model_with_tools.invoke(messages)
messages.append(response1)

# Execute tools
for tool_call in response1.tool_calls:
    result = search.invoke(tool_call)
    messages.append(result)

# Second call: model uses tool results
response2 = model_with_tools.invoke(messages)
print(response2.content)  # Answer based on search results

# Continue conversation
messages.append(response2)
messages.append({"role": "user", "content": "Tell me more"})

response3 = model_with_tools.invoke(messages)
# Model can call tools again if needed
```
</ex-tool-calling-in-conversation>

<ex-async-tool-calling>
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import asyncio

@tool
async def async_search(query: str) -> str:
    """Async search tool."""
    # Simulate async API call
    await asyncio.sleep(1)
    return f"Results for: {query}"

async def main():
    model = ChatOpenAI(model="gpt-4.1")
    model_with_tools = model.bind_tools([async_search])

    # Use ainvoke for async
    response = await model_with_tools.ainvoke("Search for Python")

    # Execute async tools
    tool_results = []
    for tool_call in response.tool_calls:
        result = await async_search.ainvoke(tool_call)
        tool_results.append(result)

    return tool_results

asyncio.run(main())
```
</ex-async-tool-calling>

<boundaries>
### What You CAN Configure

* Which tools are available**: bind_tools([tool1, tool2])
* Tool choice strategy**: auto, any, specific tool, none
* Tool execution logic**: Custom error handling, retries
* Tool parameters**: Via tool schema and type hints
* Multiple tool calls**: Models can call multiple tools

### What You CANNOT Configure

* Force model reasoning**: Can't control how model decides
* Tool call order**: Model decides (can call in parallel)
* Prevent all tool calls**: Use tool_choice or don't bind tools
* Modify tool call after model generates**: Tool calls are immutable
</boundaries>

<fix-forgetting-to-pass-tool-results-back>
```python
# WRONG: Problem: Not passing tool results back to model
response1 = model_with_tools.invoke(messages)
tool_result = tool.invoke(response1.tool_calls[0])
# Missing: passing result back to model!

# CORRECT: Solution: Always pass results back
messages.append(response1)  # AI message with tool calls
messages.append(tool_result)  # Tool result
response2 = model_with_tools.invoke(messages)
```
</fix-forgetting-to-pass-tool-results-back>

<fix-tool-call-id-mismatch>
```python
# WRONG: Problem: Wrong tool_call_id
response = model_with_tools.invoke("Get weather")
tool_message = ToolMessage(
    content="Sunny",
    tool_call_id="wrong_id",  # Doesn't match!
    name="get_weather",
)

# CORRECT: Solution: Use correct ID from tool call
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
# WRONG: Problem: Assuming model always calls tools
response = model_with_tools.invoke("Hello")
tool.invoke(response.tool_calls[0])  # Error if no tool calls!

# CORRECT: Solution: Check if tool calls exist
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
# WRONG: Problem: Binding tools overwrites previous binding
model = ChatOpenAI(model="gpt-4.1")
with_tool1 = model.bind_tools([tool1])
with_tool2 = with_tool1.bind_tools([tool2])  # Only has tool2!

# CORRECT: Solution: Bind all tools at once
with_both_tools = model.bind_tools([tool1, tool2])
```
</fix-binding-tools-multiple-times>

<fix-list-comprehension-with-async>
```python
# WRONG: Problem: List comprehension with async
tool_results = [
    await tool.ainvoke(tc) for tc in response.tool_calls
]  # SyntaxError!

# CORRECT: Solution: Use asyncio.gather
tool_results = await asyncio.gather(
    *[tool.ainvoke(tc) for tc in response.tool_calls]
)

# Or traditional loop
tool_results = []
for tool_call in response.tool_calls:
    result = await tool.ainvoke(tool_call)
    tool_results.append(result)
```
</fix-list-comprehension-with-async>

<fix-tool-choice-type-confusion>
```python
# WRONG: Problem: Wrong type for tool_choice
model.bind_tools([tool], tool_choice=True)  # Wrong!

# CORRECT: Solution: Use string values
model.bind_tools([tool], tool_choice="any")  # Force any tool
model.bind_tools([tool], tool_choice="tool_name")  # Force specific
model.bind_tools([tool])  # tool_choice="auto" (default)
```
</fix-tool-choice-type-confusion>

<fix-tool-schema-mismatches>
```python
# WRONG: Problem: Args don't match function signature
@tool
def get_weather(location: str, units: str = "celsius") -> str:
    """Get weather."""
    return f"Weather in {location}"

# Model calls: {"location": "NYC", "unit": "fahrenheit"}  # Wrong key!

# CORRECT: Solution: Match parameter names exactly
# Model will call: {"location": "NYC", "units": "fahrenheit"}
# Or use Field() for better descriptions
from pydantic import Field

@tool
def get_weather(
    location: str = Field(description="City name"),
    units: str = Field(default="celsius", description="celsius or fahrenheit")
) -> str:
    """Get weather for a location."""
    return f"Weather in {location} ({units})"
```
</fix-tool-schema-mismatches>

<links>
- [Tool Calling Overview](https://docs.langchain.com/oss/python/langchain/models)
- [Tool Calls in Messages](https://docs.langchain.com/oss/python/langchain/messages)
- [Tools Guide](https://docs.langchain.com/oss/python/langchain/tools)
- [OpenAI Tool Calling](https://docs.langchain.com/oss/python/integrations/chat/openai)
</links>
