TypeScript with fs/promises:

```typescript
import fs from "fs/promises";

const writeFile = tool(
  async ({ filepath, content }) => {
    await fs.writeFile(filepath, content, "utf-8");
    return `Successfully wrote ${content.length} characters to ${filepath}`;
  },
  {
    name: "write_file",
    description: "Write content to a file. Use carefully as this modifies the filesystem.",
    schema: z.object({
      filepath: z.string().describe("Path to the file"),
      content: z.string().describe("Content to write"),
    }),
  }
);
```
