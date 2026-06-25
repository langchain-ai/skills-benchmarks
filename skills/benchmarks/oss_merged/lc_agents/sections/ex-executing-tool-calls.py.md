Execute tool calls from the model response and pass results back for final answer.
```python
from langchain_core.messages import ToolMessage

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
