Create ToolMessage with correct tool_call_id.

```typescript
import { ToolMessage } from "langchain";

// Tool messages link back to the tool call that requested them
const toolMessage = new ToolMessage({
  content: "Weather in Paris: Sunny, 72F",
  tool_call_id: "call_abc123", // Must match AIMessage tool_call id
  name: "get_weather", // Tool name
});

// Or created automatically by tool.invoke()
const result = await getTool.invoke({
  name: "get_weather",
  args: { location: "Paris" },
  id: "call_abc123",
});
// result is a ToolMessage with proper structure
```
