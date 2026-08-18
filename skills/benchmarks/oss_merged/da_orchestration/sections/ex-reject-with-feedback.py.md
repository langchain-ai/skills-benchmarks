Reject a pending action with feedback, prompting the agent to try a different approach.
```python
agent.update_state(
    config,
    {"messages": [Command(resume={"decisions": [{"type": "reject", "message": "Run tests first"}]})]}
)
result = agent.invoke(None, config=config)
```
