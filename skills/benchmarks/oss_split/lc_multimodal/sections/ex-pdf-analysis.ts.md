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
