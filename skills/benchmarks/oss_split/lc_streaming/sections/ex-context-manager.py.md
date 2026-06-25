Use context manager for cleanup:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

# Using context manager for cleanup
with agent.stream(
    {"messages": [{"role": "user", "content": "Search something"}]},
    stream_mode=["updates"],
) as stream:
    for mode, chunk in stream:
        print(chunk)
        if some_condition:
            break  # Properly cleaned up
```
