Provide backend for skill loading:

```python
# Skills won't load without backend
agent = create_deep_agent(
    skills=["./skills/"]
)

# Provide backend
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
