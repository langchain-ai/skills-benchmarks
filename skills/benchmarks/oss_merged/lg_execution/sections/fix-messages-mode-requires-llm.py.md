Messages stream mode requires an LLM to be invoked.
```python
# WRONG: No LLM called - nothing streamed
def node(state):
    return {"output": "static text"}

# CORRECT
def node(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```
