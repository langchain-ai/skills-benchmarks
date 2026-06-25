Identify objects in image with Gemini.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "What objects are in this image?"},
    {"type": "image", "url": "https://example.com/scene.jpg"},
])

response = model.invoke([message])
```
