Load local image as base64 for GPT-4.1.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64

model = ChatOpenAI(model="gpt-4.1")

# Read image and convert to base64
with open("./photo.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Describe this image in detail"},
    {
        "type": "image",
        "base64": base64_image,
        "mime_type": "image/jpeg",
    },
])

response = model.invoke([message])
```
