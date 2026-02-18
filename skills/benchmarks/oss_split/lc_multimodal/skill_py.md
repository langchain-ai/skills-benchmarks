---
name: LangChain Multimodal (Python)
description: [LangChain] Work with multimodal inputs/outputs in LangChain - includes images, audio, video, content blocks, and vision capabilities
---

# langchain-multimodal (Python)

## Overview

Multimodal support lets you work with images, audio, video, and other non-text data. Models with multimodal capabilities can process and generate content across these different formats.

**Key Concepts:**
- **Content Blocks**: Structured representation of multimodal data
- **Vision**: Image understanding with GPT-4V, Claude, Gemini
- **Audio/Video**: Emerging support in newer models
- **Standard Format**: Cross-provider content block structure

## Code Examples

### Basic Image Input (URL)

```python
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage

model = ChatOpenAI(model="gpt-4.1")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "What's in this image?"},
    {"type": "image", "url": "https://example.com/photo.jpg"},
])

response = model.invoke([message])
print(response.content)
```

### Base64 Image Input

```python
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
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

### Multiple Images

```python
message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Compare these two images"},
    {"type": "image", "url": "https://example.com/image1.jpg"},
    {"type": "image", "url": "https://example.com/image2.jpg"},
])
```

### PDF Document Analysis

```python
from langchain_anthropic import ChatAnthropic
from langchain.schema.messages import HumanMessage
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

### Accessing Multimodal Output

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

### Vision with Claude

```python
from langchain_anthropic import ChatAnthropic
from langchain.schema.messages import HumanMessage

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

message = HumanMessage(content_blocks=[
    {"type": "image", "url": "https://example.com/chart.png"},
    {"type": "text", "text": "Extract all data points from this chart"},
])

response = model.invoke([message])
```

### Vision with Gemini

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "What objects are in this image?"},
    {"type": "image", "url": "https://example.com/scene.jpg"},
])

response = model.invoke([message])
```

## Gotchas

### 1. Model Doesn't Support Multimodal

```python
# ❌ Problem: Using text-only model
model = ChatOpenAI(model="gpt-3.5-turbo")
model.invoke([image_message])  # Error!

# ✅ Solution: Use vision-capable model
model = ChatOpenAI(model="gpt-4.1")
```

### 2. Missing MIME Type for Base64

```python
# ❌ Problem: No MIME type
{"type": "image", "base64": base64_data}  # May fail

# ✅ Solution: Always include MIME type
{"type": "image", "base64": base64_data, "mime_type": "image/jpeg"}
```

### 3. Image Too Large

```python
# ❌ Problem: Image exceeds size limit
with open("./10mb_image.jpg", "rb") as f:
    huge_image = f.read()  # Too large

# ✅ Solution: Resize images first
from PIL import Image
import io

img = Image.open("./10mb_image.jpg")
img.thumbnail((1024, 1024))
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=80)
resized_data = base64.b64encode(buffer.getvalue()).decode()
```

## Links to Documentation

- [Multimodal Guide](https://docs.langchain.com/oss/python/langchain/models)
- [Messages & Content Blocks](https://docs.langchain.com/oss/python/langchain/messages)
