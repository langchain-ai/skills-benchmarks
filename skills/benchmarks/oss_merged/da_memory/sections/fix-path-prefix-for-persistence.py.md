Path must match CompositeBackend route prefix for persistence.
```python
# With routes={"/memories/": StoreBackend(rt)}:
agent.invoke(...)  # /prefs.txt -> ephemeral (no match)
agent.invoke(...)  # /memories/prefs.txt -> persistent (matches route)
```
