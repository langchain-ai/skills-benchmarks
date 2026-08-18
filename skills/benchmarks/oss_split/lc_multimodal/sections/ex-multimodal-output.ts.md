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
