Execute tools and pass results back.

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
