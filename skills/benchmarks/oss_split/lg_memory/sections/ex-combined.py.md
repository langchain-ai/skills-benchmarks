Use both memory types together:

```python
def smart_node(state, *, store):
    # Short-term: conversation context
    recent_messages = state["messages"][-5:]  # Last 5 messages

    # Long-term: user profile
    user_id = state["user_id"]
    profile = store.get((user_id, "profile"), "info")

    # Use both for personalized response
    response = generate_response(recent_messages, profile)

    return {"messages": [response]}

graph = (
    StateGraph(State)
    .add_node("respond", smart_node)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer, store=store)
)
```
