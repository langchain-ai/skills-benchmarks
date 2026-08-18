Edit tool arguments before execution.

```python
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {"to": "alice@company.com", "subject": "Updated", "body": "..."}
            },
        }]
    }),
    config=config
)
```
