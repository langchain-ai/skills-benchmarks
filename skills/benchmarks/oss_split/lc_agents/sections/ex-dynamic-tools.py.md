Tools that depend on runtime state:

```python
def get_tools(state):
    """Tools can depend on current state."""
    user_id = state.get("config", {}).get("configurable", {}).get("user_id")
    return [get_user_specific_tool(user_id), common_tool]

agent = create_agent(model="gpt-4.1", tools=get_tools)  # Pass function instead of list
```
