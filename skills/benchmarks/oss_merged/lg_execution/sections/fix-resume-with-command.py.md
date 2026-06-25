Use Command to resume from an interrupt (regular dict restarts graph).
```python
# WRONG
graph.invoke({"resume_data": "approve"}, config)

# CORRECT
graph.invoke(Command(resume="approve"), config)
```
