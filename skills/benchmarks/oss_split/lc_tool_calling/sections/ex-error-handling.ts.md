Handle tool errors gracefully.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { ToolMessage } from "langchain";

const riskyTool = tool(
  async ({ data }) => {
    if (!data) throw new Error("Missing data");
    return "Success";
  },
  {
    name: "risky_tool",
    description: "A tool that might fail",
    schema: z.object({ data: z.string().optional() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([riskyTool]);

const response = await modelWithTools.invoke("Process this");

// Execute tools with error handling
const toolResults = [];
for (const toolCall of response.tool_calls || []) {
  try {
    const result = await riskyTool.invoke(toolCall);
    toolResults.push(result);
  } catch (error) {
    // Return error as tool message
    toolResults.push(
      new ToolMessage({
        content: `Error: ${error.message}`,
        tool_call_id: toolCall.id,
        name: toolCall.name,
      })
    );
  }
}
```
