Multi-turn conversation with tool calls.

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
