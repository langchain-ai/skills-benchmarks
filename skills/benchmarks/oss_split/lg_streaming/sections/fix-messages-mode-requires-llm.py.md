LLM call required for token streaming:

```python
# WRONG - No LLM called, nothing streamed
def node(state):
    return {"output": "static text"}

for chunk in graph.stream({}, stream_mode="messages"):
    print(chunk)  # Nothing!

# CORRECT - LLM invoked
def node(state):
    response = model.invoke(state["messages"])  # LLM call
    return {"messages": [response]}
```
