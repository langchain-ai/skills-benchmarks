Stream tokens and progress together:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

# Stream both LLM tokens AND agent progress
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research LangChain"}]},
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        # LLM token stream
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        # Agent step updates
        print(f"\nStep update: {chunk}")
```
