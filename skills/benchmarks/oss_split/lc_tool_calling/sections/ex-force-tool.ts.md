Force model to use a specific tool.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const extractInfo = tool(
  async ({ name, email }) => ({ name, email }),
  {
    name: "extract_info",
    description: "Extract name and email",
    schema: z.object({
      name: z.string(),
      email: z.string(),
    }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });

// Force model to use this specific tool
const modelWithTools = model.bindTools([extractInfo], {
  tool_choice: "extract_info", // Must use this tool
});

const response = await modelWithTools.invoke(
  "Contact: John Doe (john@example.com)"
);

// Model always calls extract_info
console.log(response.tool_calls[0].args);
// { name: "John Doe", email: "john@example.com" }
```
