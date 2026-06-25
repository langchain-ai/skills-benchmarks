Compare two images in one message.

```python
message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Compare these two images"},
    {"type": "image", "url": "https://example.com/image1.jpg"},
    {"type": "image", "url": "https://example.com/image2.jpg"},
])
```
