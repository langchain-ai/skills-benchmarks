Emit custom progress from tools:

```typescript
import { tool } from "langchain";
import { z } from "zod";

const processData = tool(
  async ({ data }, { runtime }) => {
    const total = data.length;

    for (let i = 0; i < total; i += 100) {
      // Emit custom progress update
      await runtime.stream_writer.write({
        type: "progress",
        data: {
          processed: i,
          total: total,
          percentage: (i / total) * 100,
        },
      });

      // Do actual processing
      await processChunk(data.slice(i, i + 100));
    }

    return "Processing complete";
  },
  {
    name: "process_data",
    description: "Process data with progress updates",
    schema: z.object({
      data: z.array(z.any()),
    }),
  }
);

// Stream custom updates
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Process this data" }] },
  { streamMode: ["custom", "updates"] }
)) {
  if (mode === "custom") {
    console.log(`Progress: ${chunk.data.percentage}%`);
  }
}
```
