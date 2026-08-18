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
