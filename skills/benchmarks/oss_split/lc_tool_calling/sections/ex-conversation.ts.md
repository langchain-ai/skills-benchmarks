Multi-turn conversation with tool calls.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const searchTool = tool(
  async ({ query }) => `Results for: ${query}`,
  {
    name: "search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([searchTool]);

const messages = [
  { role: "user", content: "Search for LangChain" },
];

// First call: model decides to use tool
const response1 = await modelWithTools.invoke(messages);
messages.push(response1);

// Execute tools
for (const toolCall of response1.tool_calls || []) {
  const result = await searchTool.invoke(toolCall);
  messages.push(result);
}

// Second call: model uses tool results
const response2 = await modelWithTools.invoke(messages);
console.log(response2.content); // Answer based on search results

// Continue conversation
messages.push(response2);
messages.push({ role: "user", content: "Tell me more" });

const response3 = await modelWithTools.invoke(messages);
// Model can call tools again if needed
```
