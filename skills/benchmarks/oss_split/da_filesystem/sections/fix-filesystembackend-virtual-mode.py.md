Enable virtual_mode to restrict paths:

```python
# Insecure - agent can access anywhere
backend = FilesystemBackend(root_dir="/project", virtual_mode=False)

# Secure - agent restricted to /project
backend = FilesystemBackend(root_dir="/project", virtual_mode=True)
```
