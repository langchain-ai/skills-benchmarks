Stream agent steps with updates mode:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool, calculator_tool],
)

# Stream agent steps with "updates" mode
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize"}]},
    stream_mode=["updates"],
):
    print(f"Step: {chunk}")
# Shows each step: model call, tool execution, final response
```
