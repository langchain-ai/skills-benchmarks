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
