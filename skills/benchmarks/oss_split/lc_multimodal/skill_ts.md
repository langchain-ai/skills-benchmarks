---
name: LangChain Multimodal (TypeScript)
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

<model-selection-table>

| Task | Recommended Model | Why |
|------|------------------|-----|
| Image understanding | GPT-4.1, Claude Sonnet, Gemini | Strong vision capabilities |
| Image generation | DALL-E (via OpenAI) | Specialized for generation |
| Document analysis (PDF) | Claude, GPT-4.1 | Handle complex layouts |
| Audio transcription | Whisper (OpenAI) | Specialized for audio |

</model-selection-table>

<input-methods-table>

| Method | When to Use | Example |
|--------|-------------|---------|
| URL | Public images | `{ type: "image", url: "https://..." }` |
| Base64 | Private/local images | `{ type: "image", data: "base64..." }` |
| File reference | Provider file APIs | `{ type: "image", fileId: "..." }` |

</input-methods-table>

<ex-basic-image-url>
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
</ex-basic-image-url>

<ex-base64-image>
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
</ex-base64-image>

<ex-multiple-images>
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
</ex-multiple-images>

<ex-pdf-analysis>
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
</ex-pdf-analysis>

<ex-audio-input>
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
</ex-audio-input>

<ex-multimodal-output>
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
</ex-multimodal-output>

<ex-vision-claude>
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
</ex-vision-claude>

<ex-vision-gemini>
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
</ex-vision-gemini>

<boundaries>
**What You CAN Do**

* Image URLs**: Public images via HTTPS
* Base64 images**: Local or private images
* Multiple images**: Compare, analyze together
* PDF documents**: Text extraction, analysis
* Cross-provider format**: Standard content blocks

**What You CANNOT Do (Yet)**

* Image generation in all models**: Limited to specific models
* Video understanding**: Emerging, limited support
* Audio in all models**: Model-specific
* Modify images**: Models analyze, don't edit
</boundaries>

<fix-model-doesnt-support-multimodal>
```typescript
// Problem: Using text-only model
const model = new ChatOpenAI({ model: "gpt-3.5-turbo" });
await model.invoke([imageMessage]);  // Error!

// Solution: Use vision-capable model
const model = new ChatOpenAI({ model: "gpt-4.1" });
```
</fix-model-doesnt-support-multimodal>

<fix-wrong-content-block-format>
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
</fix-wrong-content-block-format>

<fix-missing-mime-type>
```typescript
// Problem: No MIME type
{ type: "image", data: base64Data }  // May fail

// Solution: Always include MIME type
{ type: "image", data: base64Data, mimeType: "image/jpeg" }
```
</fix-missing-mime-type>

<fix-image-too-large>
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
</fix-image-too-large>

<documentation-links>
- [Multimodal Guide](https://docs.langchain.com/oss/javascript/langchain/models)
- [Messages & Content Blocks](https://docs.langchain.com/oss/javascript/langchain/messages)
- [OpenAI Vision](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
- [Anthropic Vision](https://docs.langchain.com/oss/javascript/integrations/chat/anthropic)
</documentation-links>
