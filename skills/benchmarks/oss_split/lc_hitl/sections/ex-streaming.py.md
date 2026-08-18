Stream responses with interrupt handling.

```python
# Stream until interrupt
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Send report to team"}]},
    config=config,
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        if "__interrupt__" in chunk:
            print("\nWaiting for approval...")
            break

# Resume after approval
for mode, chunk in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode=["messages"],
):
    # Continue streaming
    pass
```
