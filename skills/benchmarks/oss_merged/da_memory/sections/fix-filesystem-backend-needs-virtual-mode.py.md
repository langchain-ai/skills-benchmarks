Enable virtual_mode=True to restrict path access (prevents ../ and ~/ escapes).
```python
backend = FilesystemBackend(root_dir="/project", virtual_mode=True)  # Secure
```
