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
