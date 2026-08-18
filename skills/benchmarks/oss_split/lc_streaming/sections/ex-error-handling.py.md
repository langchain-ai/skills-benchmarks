Handle errors during streaming:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[risky_tool],
)

try:
    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Do risky operation"}]},
        stream_mode=["updates"],
    ):
        # Check for errors in updates
        if "__error__" in chunk:
            print(f"Error in stream: {chunk['__error__']}")
            break

        print(f"Update: {chunk}")
except Exception as error:
    print(f"Stream error: {error}")
```
