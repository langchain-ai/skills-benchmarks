Stream agent steps and tokens:

```python
# Stream with updates mode to see each step
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for LangChain"}]},
    stream_mode=["updates"],
):
    print(f"Step: {chunk}")

# Stream with messages mode for LLM tokens
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for LangChain"}]},
    stream_mode=["messages"],
):
    token, metadata = chunk
    if token.content:
        print(token.content, end="", flush=True)
```
