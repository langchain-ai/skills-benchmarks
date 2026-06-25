Use correct parameter names from schema:

```python
# Edited args must match tool schema
agent.update_state(config, {
    "messages": [Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {"name": "execute_sql", "args": {"wrong_param": "value"}}  # Tool doesn't have this param
        }]
    })]
})

# Use correct parameter names from tool schema
```
