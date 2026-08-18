Customize filesystem tool descriptions:

```typescript
import { createAgent, createFilesystemMiddleware } from "langchain";

const agent = createAgent({
  model: "claude-sonnet-4-5-20250929",
  middleware: [
    createFilesystemMiddleware({
      systemPrompt: "Save intermediate results to /workspace/",
      customToolDescriptions: {
        read_file: "Read files you've previously written. Use offset/limit for large files.",
        write_file: "Save data to avoid context overflow.",
      }
    }),
  ],
});
```
