---
name: langchain-multimodal
description: "[LangChain] Work with multimodal inputs/outputs in LangChain - includes images, audio, video, content blocks, and vision capabilities"
---

<oneliner>
Work with multimodal inputs/outputs in LangChain including images, audio, video, content blocks, and vision capabilities with GPT-4V, Claude, and Gemini.
</oneliner>

<overview>
Multimodal support lets you work with images, audio, video, and other non-text data. Models with multimodal capabilities can process and generate content across these different formats.

Key Concepts:
- **Content Blocks**: Structured representation of multimodal data
- **Vision**: Image understanding with GPT-4V, Claude, Gemini
- **Audio/Video**: Emerging support in newer models
- **Standard Format**: Cross-provider content block structure
</overview>

<model-selection-for-multimodal>

| Task | Recommended Model | Why |
|------|------------------|-----|
| Image understanding | GPT-4.1, Claude Sonnet, Gemini | Strong vision capabilities |
| Image generation | DALL-E (via OpenAI) | Specialized for generation |
| Document analysis (PDF) | Claude, GPT-4.1 | Handle complex layouts |
| Audio transcription | Whisper (OpenAI) | Specialized for audio |

</model-selection-for-multimodal>

<input-methods>

| Method | When to Use | Example |
|--------|-------------|---------|
| URL | Public images | `{ type: "image", url: "https://..." }` |
| Base64 | Private/local images | `{ type: "image", data: "base64..." }` / `{ "type": "image", "base64": "..." }` |
| File reference | Provider file APIs | `{ type: "image", fileId: "..." }` |

</input-methods>

<ex-image-url>
<python>
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
</python>

<typescript>
Send image URL to GPT-4.1 for analysis.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "langchain";

const model = new ChatOpenAI({ model: "gpt-4.1" });

const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "What's in this image?" },
    {
      type: "image",
      url: "https://example.com/photo.jpg",
    },
  ],
});

const response = await model.invoke([message]);
console.log(response.content);
```
</typescript>
</ex-image-url>

<ex-image-base64>
<python>
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
</python>

<typescript>
Load local image as base64 for GPT-4.1.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "langchain";
import fs from "fs";

const model = new ChatOpenAI({ model: "gpt-4.1" });

// Read image and convert to base64
const imageBuffer = fs.readFileSync("./photo.jpg");
const base64Image = imageBuffer.toString("base64");

const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "Describe this image in detail" },
    {
      type: "image",
      data: base64Image,
      mimeType: "image/jpeg",
    },
  ],
});

const response = await model.invoke([message]);
```
</typescript>
</ex-image-base64>

<ex-multiple-images>
<python>
Compare two images in one message.

```python
message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Compare these two images"},
    {"type": "image", "url": "https://example.com/image1.jpg"},
    {"type": "image", "url": "https://example.com/image2.jpg"},
])
```
</python>

<typescript>
Compare two images in one message.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "langchain";

const model = new ChatOpenAI({ model: "gpt-4.1" });

const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "Compare these two images" },
    { type: "image", url: "https://example.com/image1.jpg" },
    { type: "image", url: "https://example.com/image2.jpg" },
  ],
});

const response = await model.invoke([message]);
```
</typescript>
</ex-multiple-images>

<ex-pdf-analysis>
<python>
Analyze PDF document with Claude.

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
</python>

<typescript>
Analyze PDF document with Claude.

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { HumanMessage } from "langchain";
import fs from "fs";

const model = new ChatAnthropic({ model: "claude-sonnet-4-5-20250929" });

const pdfBuffer = fs.readFileSync("./document.pdf");
const base64Pdf = pdfBuffer.toString("base64");

const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "Summarize this PDF document" },
    {
      type: "file",
      data: base64Pdf,
      mimeType: "application/pdf",
    },
  ],
});

const response = await model.invoke([message]);
```
</typescript>
</ex-pdf-analysis>

<ex-audio-input>
<typescript>
Send audio content for transcription.

```typescript
// Example with hypothetical audio support
const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "Transcribe this audio" },
    {
      type: "audio",
      data: base64Audio,
      mimeType: "audio/mpeg",
    },
  ],
});
```
</typescript>
</ex-audio-input>

<ex-multimodal-output>
<python>
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
</python>

<typescript>
Handle text and image content blocks in response.

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

const response = await model.invoke("Create an image of a sunset");

// Access content blocks
for (const block of response.contentBlocks) {
  if (block.type === "text") {
    console.log("Text:", block.text);
  } else if (block.type === "image") {
    console.log("Image URL:", block.url);
    console.log("Image data:", block.data?.substring(0, 50) + "...");
  }
}
```
</typescript>
</ex-multimodal-output>

<ex-vision-claude>
<python>
Extract data from chart image with Claude.

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
</python>

<typescript>
Extract data from chart image with Claude.

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { HumanMessage } from "langchain";

const model = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
});

const message = new HumanMessage({
  contentBlocks: [
    {
      type: "image",
      url: "https://example.com/chart.png",
    },
    {
      type: "text",
      text: "Extract all data points from this chart and format as a table",
    },
  ],
});

const response = await model.invoke([message]);
```
</typescript>
</ex-vision-claude>

<ex-vision-gemini>
<python>
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
</python>

<typescript>
Identify objects in image with Gemini.

```typescript
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { HumanMessage } from "langchain";

const model = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash",
});

const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "What objects are in this image?" },
    { type: "image", url: "https://example.com/scene.jpg" },
  ],
});

const response = await model.invoke([message]);
```
</typescript>
</ex-vision-gemini>

<boundaries>
What You CAN Do:
- **Image URLs**: Public images via HTTPS
- **Base64 images**: Local or private images
- **Multiple images**: Compare, analyze together
- **PDF documents**: Text extraction, analysis
- **Cross-provider format**: Standard content blocks

What You CANNOT Do (Yet):
- **Image generation in all models**: Limited to specific models
- **Video understanding**: Emerging, limited support
- **Audio in all models**: Model-specific
- **Modify images**: Models analyze, don't edit
</boundaries>

<fix-model-support>
<python>
Switch from text-only to vision-capable model.

```python
# Problem: Using text-only model
model = ChatOpenAI(model="gpt-3.5-turbo")
model.invoke([image_message])  # Error!

# Solution: Use vision-capable model
model = ChatOpenAI(model="gpt-4.1")
```
</python>
<typescript>
Switch from text-only to vision-capable model.

```typescript
// Problem: Using text-only model
const model = new ChatOpenAI({ model: "gpt-3.5-turbo" });
await model.invoke([imageMessage]);  // Error!

// Solution: Use vision-capable model
const model = new ChatOpenAI({ model: "gpt-4.1" });
```
</typescript>
</fix-model-support>

<fix-content-block-format>
<typescript>
Use standard contentBlocks instead of old format.

```typescript
// Problem: Old format
const message = new HumanMessage({
  content: [
    { type: "image_url", image_url: { url: "..." } }  // OpenAI-specific
  ]
});

// Solution: Use standard content blocks
const message = new HumanMessage({
  contentBlocks: [
    { type: "image", url: "..." }  // Cross-provider
  ]
});
```
</typescript>
</fix-content-block-format>

<fix-mime-type>
<python>
Always include mime_type with base64 data.

```python
# Problem: No MIME type
{"type": "image", "base64": base64_data}  # May fail

# Solution: Always include MIME type
{"type": "image", "base64": base64_data, "mime_type": "image/jpeg"}
```
</python>
<typescript>
Always include mimeType with base64 data.

```typescript
// Problem: No MIME type
{ type: "image", data: base64Data }  // May fail

// Solution: Always include MIME type
{ type: "image", data: base64Data, mimeType: "image/jpeg" }
```
</typescript>
</fix-mime-type>

<fix-image-size>
<python>
Resize large images with PIL before sending.

```python
# Problem: Image exceeds size limit
with open("./10mb_image.jpg", "rb") as f:
    huge_image = f.read()  # Too large

# Solution: Resize images first
from PIL import Image
import io

img = Image.open("./10mb_image.jpg")
img.thumbnail((1024, 1024))
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=80)
resized_data = base64.b64encode(buffer.getvalue()).decode()
```
</python>
<typescript>
Resize large images with sharp before sending.

```typescript
// Problem: Image exceeds size limit
const hugeImage = fs.readFileSync("./10mb_image.jpg");
// Model may reject

// Solution: Resize or compress images first
import sharp from "sharp";

const resized = await sharp("./10mb_image.jpg")
  .resize(1024, 1024, { fit: "inside" })
  .jpeg({ quality: 80 })
  .toBuffer();
```
</typescript>
</fix-image-size>

<documentation-links>
Python:
- [Multimodal Guide](https://docs.langchain.com/oss/python/langchain/models)
- [Messages & Content Blocks](https://docs.langchain.com/oss/python/langchain/messages)

TypeScript:
- [Multimodal Guide](https://docs.langchain.com/oss/javascript/langchain/models)
- [Messages & Content Blocks](https://docs.langchain.com/oss/javascript/langchain/messages)
- [OpenAI Vision](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
- [Anthropic Vision](https://docs.langchain.com/oss/javascript/integrations/chat/anthropic)
</documentation-links>
