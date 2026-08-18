Stream state updates and tokens:

```python
# Stream state updates
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Calculate 5 + 3")]},
    stream_mode="updates"
):
    print(chunk)

# Stream LLM tokens
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Hello!")]},
    stream_mode="messages"
):
    print(chunk)

# Multiple stream modes
for mode, chunk in agent.stream(
    {"messages": [HumanMessage(content="Help me")]},
    stream_mode=["updates", "messages"]
):
    print(f"{mode}: {chunk}")
```
