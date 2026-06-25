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
