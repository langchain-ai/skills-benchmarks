Skills require a proper backend to load from the filesystem.
```python
# WRONG: Skills won't load without proper backend
agent = create_deep_agent(skills=["./skills/"])

# CORRECT: Use FilesystemBackend for local skills
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
