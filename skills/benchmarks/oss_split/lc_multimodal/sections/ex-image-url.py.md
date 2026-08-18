Send image URL to GPT-4.1 for analysis.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

model = ChatOpenAI(model="gpt-4.1")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "What's in this image?"},
    {"type": "image", "url": "https://example.com/photo.jpg"},
])

response = model.invoke([message])
print(response.content)
```
