Longer prefixes take precedence:

```python
# Routes are matched by longest prefix
backend = CompositeBackend(
    default=StateBackend(rt),
    routes={
        "/mem/": StoreBackend(rt),
        "/mem/temp/": StateBackend(rt),  # More specific
    }
)

# /mem/file.txt -> StoreBackend
# /mem/temp/file.txt -> StateBackend (longer match)
# /workspace/file.txt -> StateBackend (default)
```
