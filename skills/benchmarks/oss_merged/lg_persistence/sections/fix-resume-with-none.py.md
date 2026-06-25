Pass None to resume from checkpoint instead of providing new input.
```python
# WRONG: Providing new input restarts from beginning
graph.invoke({"messages": ["New message"]}, config)  # Restarts!

# CORRECT: Use None to resume from checkpoint
graph.invoke(None, config)  # Continues from where it paused
```
