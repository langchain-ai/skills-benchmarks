Provide store when using StoreBackend:

```python
# Missing store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Provide store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
