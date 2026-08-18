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
