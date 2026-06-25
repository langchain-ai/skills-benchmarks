| Type | Backend | Persistence | Use Case |
|------|---------|------------|----------|
| Short-term | StateBackend | Single thread | Temporary working files |
| Long-term | StoreBackend | Across threads | User preferences, learned patterns |
| Hybrid | CompositeBackend | Mix both | Some persistent, some temporary |
