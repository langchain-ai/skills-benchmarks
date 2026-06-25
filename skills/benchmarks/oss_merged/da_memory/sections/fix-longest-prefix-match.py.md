CompositeBackend matches longest prefix first.
```python
routes = {"/mem/": StoreBackend(rt), "/mem/temp/": StateBackend(rt)}
# /mem/file.txt -> StoreBackend, /mem/temp/file.txt -> StateBackend (longer match)
```
