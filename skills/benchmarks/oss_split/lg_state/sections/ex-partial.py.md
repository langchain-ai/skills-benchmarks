Update only specific fields:

```python
class State(TypedDict):
    field1: str
    field2: str
    field3: str

def update_field1(state: State) -> dict:
    # Only update field1, others unchanged
    return {"field1": "updated"}

def update_field2(state: State) -> dict:
    # Only update field2
    return {"field2": "also updated"}

graph = (
    StateGraph(State)
    .add_node("node1", update_field1)
    .add_node("node2", update_field2)
    .add_edge(START, "node1")
    .add_edge("node1", "node2")
    .add_edge("node2", END)
    .compile()
)

result = graph.invoke({
    "field1": "original1",
    "field2": "original2",
    "field3": "original3"
})
# field1: "updated", field2: "also updated", field3: "original3"
```
