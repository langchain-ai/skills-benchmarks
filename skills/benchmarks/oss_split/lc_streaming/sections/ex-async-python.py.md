Use astream for async contexts:

```python
from langchain.agents import create_agent
import asyncio

agent = create_agent(
    model="gpt-4.1",
    tools=[async_tool],
)

async def main():
    async for mode, chunk in agent.astream(
        {"messages": [{"role": "user", "content": "Process async"}]},
        stream_mode=["updates"],
    ):
        print(f"Update: {chunk}")

asyncio.run(main())
```
