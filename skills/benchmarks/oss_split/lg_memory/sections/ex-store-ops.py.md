Basic store CRUD operations:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Put (create/update)
store.put(
    ("user-123", "facts"),
    "location",
    {"city": "San Francisco", "country": "USA"}
)

# Get
item = store.get(("user-123", "facts"), "location")
print(item)  # {'city': 'San Francisco', 'country': 'USA'}

# Search with filters
results = store.search(
    ("user-123", "facts"),
    filter={"country": "USA"}
)

# Delete
store.delete(("user-123", "facts"), "location")
```
