Execute tools and pass results back.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { ToolMessage } from "langchain";

const getTool = tool(
  async ({ location }) => `Weather in ${location}: Sunny`,
  {
    name: "get_weather",
    description: "Get weather",
    schema: z.object({ location: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getTool]);

// Step 1: Model decides to call tool
const messages = [{ role: "user", content: "What's the weather in NYC?" }];
const response1 = await modelWithTools.invoke(messages);

// Step 2: Execute the tool
const toolResults = [];
for (const toolCall of response1.tool_calls || []) {
  const result = await getTool.invoke(toolCall);
  toolResults.push(result); // This is a ToolMessage
}

// Step 3: Pass results back to model
messages.push(response1); // Add AI message with tool calls
messages.push(...toolResults); // Add tool results

const response2 = await modelWithTools.invoke(messages);
console.log(response2.content); // Final answer using tool results
```
