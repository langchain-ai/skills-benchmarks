Handle text and image content blocks in response.

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")
response = model.invoke("Create an image of a sunset")

# Access content blocks
for block in response.content_blocks:
    if block["type"] == "text":
        print(f"Text: {block['text']}")
    elif block["type"] == "image":
        print(f"Image URL: {block.get('url')}")
        if "base64" in block:
            print(f"Image data: {block['base64'][:50]}...")
```
