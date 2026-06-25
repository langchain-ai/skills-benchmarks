Human approval for tool calls:

```typescript
import { interrupt, Command } from "@langchain/langgraph";

const toolExecutor = async (state) => {
  const toolCalls = state.messages.at(-1)?.tool_calls || [];
  const results = [];

  for (const toolCall of toolCalls) {
    // Pause for each tool call
    const userDecision = interrupt({
      tool: toolCall.name,
      args: toolCall.args,
      question: "Execute this tool?",
    });

    let result;
    if (userDecision.type === "approve") {
      // Execute tool
      result = await executeTool(toolCall);
    } else if (userDecision.type === "edit") {
      // Use edited args
      result = await executeTool(userDecision.args);
    } else {  // reject
      result = "Tool execution rejected";
    }

    // Store result
    results.push(new ToolMessage({
      content: result,
      tool_call_id: toolCall.id,
    }));
  }

  return { messages: results };
};

// Usage
const result = await graph.invoke({ messages: [...] }, config);

// Review and approve
await graph.invoke(new Command({ resume: { type: "approve" } }), config);

// Or edit args
await graph.invoke(
  new Command({ resume: { type: "edit", args: { query: "modified" } } }),
  config
);

// Or reject
await graph.invoke(new Command({ resume: { type: "reject" } }), config);
```
