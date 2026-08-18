Require human approval before executing sensitive tools like delete operations.
```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";

const deleteRecord = tool(
  async ({ recordId }) => {
    await db.delete(recordId);
    return `Deleted record ${recordId}`;
  },
  {
    name: "delete_record",
    description: "Delete a database record permanently.",
    schema: z.object({ recordId: z.string().describe("ID of record to delete") }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [deleteRecord, search],
  middleware: [
    humanInTheLoopMiddleware({
      toolsRequiringApproval: ["delete_record"],
    }),
  ],
});
```
