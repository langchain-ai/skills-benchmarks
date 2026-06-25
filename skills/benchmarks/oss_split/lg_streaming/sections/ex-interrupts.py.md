Handle interrupts during streaming:

```python
async for metadata, mode, chunk in graph.astream(
    {"query": "test"},
    stream_mode=["messages", "updates"],
    subgraphs=True,
    config={"configurable": {"thread_id": "1"}}
):
    if mode == "messages":
        # Handle streaming LLM content
        msg, _ = chunk
        if hasattr(msg, "content"):
            print(msg.content, end="")

    elif mode == "updates":
        # Check for interrupts
        if "__interrupt__" in chunk:
            # Handle interrupt
            interrupt_info = chunk["__interrupt__"][0].value
            user_input = input(f"Approve? {interrupt_info}: ")
            # Resume
            break
```
