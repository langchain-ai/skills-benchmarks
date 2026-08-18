Handle interrupts while streaming:

```python
async for mode, chunk in graph.astream(
    {"query": "test"},
    stream_mode=["updates", "messages"],
    config={"configurable": {"thread_id": "1"}}
):
    if mode == "updates":
        if "__interrupt__" in chunk:
            # Handle interrupt
            interrupt_info = chunk["__interrupt__"][0].value
            user_input = get_user_input(interrupt_info)

            # Resume
            initial_input = Command(resume=user_input)
            break
```
