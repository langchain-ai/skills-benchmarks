Edit the proposed action arguments before allowing execution.
```python
# Edit the proposed action
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "edit",
                        "edited_action": {
                            "name": "execute_sql",
                            "args": {
                                "query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
                            }
                        }
                    }]
                }
            )
        ]
    }
)

result = agent.invoke(None, config=config)
```
