Get full state after each step:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[weather_tool],
)

# Get full state after each step
for mode, state in agent.stream(
    {"messages": [{"role": "user", "content": "What's the weather?"}]},
    stream_mode=["values"],
):
    print(f"Current messages: {len(state['messages'])}")
    print(f"Last message: {state['messages'][-1].content}")
```
