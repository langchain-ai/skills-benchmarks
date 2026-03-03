---
name: langchain-multimodal-py
description: "[LangChain] Work with multimodal inputs/outputs in LangChain - includes images, audio, video, content blocks, and vision capabilities"
---

<overview>
Multimodal support lets you work with images, audio, video, and other non-text data. Models with multimodal capabilities can process and generate content across these different formats.

**Key Concepts:**
- **Content Blocks**: Structured representation of multimodal data
- **Vision**: Image understanding with GPT-4V, Claude, Gemini
- **Audio/Video**: Emerging support in newer models
- **Standard Format**: Cross-provider content block structure
</overview>

<ex-basic-image-input-url>
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
</ex-basic-image-input-url>

<ex-base64-image-input>
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
</ex-base64-image-input>

<ex-multiple-images>
```python
message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Compare these two images"},
    {"type": "image", "url": "https://example.com/image1.jpg"},
    {"type": "image", "url": "https://example.com/image2.jpg"},
])
```
</ex-multiple-images>

<ex-pdf-document-analysis>
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import base64

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

with open("./document.pdf", "rb") as pdf_file:
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Summarize this PDF document"},
    {
        "type": "file",
        "base64": base64_pdf,
        "mime_type": "application/pdf",
    },
])

response = model.invoke([message])
```
</ex-pdf-document-analysis>

<ex-accessing-multimodal-output>
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
</ex-accessing-multimodal-output>

<ex-vision-with-claude>
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

message = HumanMessage(content_blocks=[
    {"type": "image", "url": "https://example.com/chart.png"},
    {"type": "text", "text": "Extract all data points from this chart"},
])

response = model.invoke([message])
```
</ex-vision-with-claude>

<ex-vision-with-gemini>
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
</ex-vision-with-gemini>

<fix-model-doesnt-support-multimodal>
```python
# WRONG: Problem: Using text-only model
model = ChatOpenAI(model="gpt-3.5-turbo")
model.invoke([image_message])  # Error!

# CORRECT: Solution: Use vision-capable model
model = ChatOpenAI(model="gpt-4.1")
```
</fix-model-doesnt-support-multimodal>

<fix-missing-mime-type-for-base64>
```python
# WRONG: Problem: No MIME type
{"type": "image", "base64": base64_data}  # May fail

# CORRECT: Solution: Always include MIME type
{"type": "image", "base64": base64_data, "mime_type": "image/jpeg"}
```
</fix-missing-mime-type-for-base64>

<fix-image-too-large>
```python
# WRONG: Problem: Image exceeds size limit
with open("./10mb_image.jpg", "rb") as f:
    huge_image = f.read()  # Too large

# CORRECT: Solution: Resize images first
from PIL import Image
import io

img = Image.open("./10mb_image.jpg")
img.thumbnail((1024, 1024))
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=80)
resized_data = base64.b64encode(buffer.getvalue()).decode()
```
</fix-image-too-large>

<links>
- [Multimodal Guide](https://docs.langchain.com/oss/python/langchain/models)
- [Messages & Content Blocks](https://docs.langchain.com/oss/python/langchain/messages)
</links>
