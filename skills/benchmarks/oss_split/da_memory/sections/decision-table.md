| Pattern | Backend Setup | Use Case |
|---------|--------------|----------|
| All ephemeral | StateBackend | Single-session tasks |
| All persistent | StoreBackend | Everything remembered |
| Hybrid | CompositeBackend | `/memories/` persistent, rest ephemeral |
| Custom routing | CompositeBackend with multiple routes | Complex storage needs |
