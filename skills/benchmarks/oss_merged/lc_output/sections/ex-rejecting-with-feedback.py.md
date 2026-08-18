Reject a tool call and provide feedback explaining why it was rejected.
```python
# Human rejects
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "reject",
            "feedback": "Cannot delete customer data without manager approval",
        }]
    }),
    config=config
)
```
