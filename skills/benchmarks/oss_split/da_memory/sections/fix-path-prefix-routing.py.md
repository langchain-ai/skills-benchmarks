Use correct path prefix for persistence:

```python
# Won't be persistent (wrong path)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /prefs.txt"}]
})

# Persistent (matches /memories/ route)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /memories/prefs.txt"}]
})
```
