Use None to resume from checkpoint:

```python
# WRONG - Providing input restarts
graph.invoke({"new": "data"}, config)  # Restarts from beginning

# CORRECT - Use None to resume
graph.invoke(None, config)  # Resumes from checkpoint
```
