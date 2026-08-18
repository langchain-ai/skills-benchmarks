Compile-time breakpoints:

```python
checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_node("step3", step3)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", "step3")
    .add_edge("step3", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"],  # Pause before step2
        interrupt_after=["step3"]    # Pause after step3
    )
)

config = {"configurable": {"thread_id": "1"}}

# Run until first breakpoint
graph.invoke({"data": "test"}, config)

# Resume (pauses at next breakpoint)
graph.invoke(None, config)  # None = resume

# Resume again
graph.invoke(None, config)
```
