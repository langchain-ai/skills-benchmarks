Match whitespace exactly from file:

```python
# The edit_file tool needs exact string matching

# Won't work - whitespace mismatch
old_string = "def hello():\n  print('hi')"
new_string = "def hello():\n    print('hi')"  # Different indentation

# Match exactly as it appears in the file
old_string = "  print('hi')"  # Exact match from file
new_string = "    print('hi')"  # New content
```
