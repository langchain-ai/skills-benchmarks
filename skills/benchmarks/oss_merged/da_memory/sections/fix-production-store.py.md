Use PostgresStore for production (InMemoryStore lost on restart).
```python
# WRONG                              # CORRECT
store = InMemoryStore()              store = PostgresStore(connection_string="postgresql://...")
```
