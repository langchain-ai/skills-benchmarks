TypeScript with runtime context:

```typescript
const processLargeFile = tool(
  async ({ filepath }, { runtime }) => {
    const totalLines = 1000;

    for (let i = 0; i < totalLines; i += 100) {
      await runtime.stream_writer.write({
        type: "progress",
        data: { processed: i, total: totalLines },
      });
      await processChunk(i, i + 100);
    }

    return "Processing complete";
  },
  {
    name: "process_file",
    description: "Process a large file with progress updates",
    schema: z.object({ filepath: z.string() }),
  }
);
```
