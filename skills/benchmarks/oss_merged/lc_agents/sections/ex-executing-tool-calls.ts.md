Execute tool calls from the model response and pass results back for final answer.
```typescript
import { ToolMessage } from "@langchain/core/messages";

// Step 1: Model decides to call tool
const messages = [{ role: "user", content: "What's the weather in NYC?" }];
const response1 = await modelWithTools.invoke(messages);

// Step 2: Execute the tool
const toolResults = [];
for (const toolCall of response1.tool_calls ?? []) {
  const result = await getWeather.invoke(toolCall.args);
  toolResults.push(new ToolMessage({ content: result, tool_call_id: toolCall.id }));
}

// Step 3: Pass results back to model
messages.push(response1);
messages.push(...toolResults);

const response2 = await modelWithTools.invoke(messages);
console.log(response2.content);
```
