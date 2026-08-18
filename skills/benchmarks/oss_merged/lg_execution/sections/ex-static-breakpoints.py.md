Set compile-time breakpoints for debugging. Not recommended for human-in-the-loop — use `interrupt()` instead.
```python
graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"],  # Pause before step2
    )
)

config = {"configurable": {"thread_id": "1"}}
graph.invoke({"data": "test"}, config)  # Runs until step2
graph.invoke(None, config)  # Resume
```
