Reject tool call with feedback.

```python
result2 = agent.invoke(
    Command(resume={
        "decisions": [{"type": "reject", "feedback": "Cannot delete without manager approval"}]
    }),
    config=config
)
```
