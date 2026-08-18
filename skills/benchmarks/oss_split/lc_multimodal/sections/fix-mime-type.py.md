Always include mime_type with base64 data.

```python
# Problem: No MIME type
{"type": "image", "base64": base64_data}  # May fail

# Solution: Always include MIME type
{"type": "image", "base64": base64_data, "mime_type": "image/jpeg"}
```
