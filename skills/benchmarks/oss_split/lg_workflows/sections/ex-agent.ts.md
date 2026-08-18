Tool-calling agent with dynamic routing:

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";
import { AIMessage, ToolMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, END, START } from "@langchain/langgraph";
import { z } from "zod";

const search = tool(async ({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

const calculate = tool(async ({ a, b, op }) => {
  const ops: Record<string, number> = { add: a + b, subtract: a - b, multiply: a * b, divide: a / b };
  return (ops[op] ?? "Invalid operation").toString();
}, {
  name: "calculate",
  description: "Calculate a mathematical expression",
  schema: z.object({ a: z.number(), b: z.number(), op: z.string() }),
});

const AgentState = new StateSchema({
  messages: MessagesValue,
});

const model = new ChatAnthropic({ model: "claude-sonnet-4-5-20250929" });
const tools = [search, calculate];
const modelWithTools = model.bindTools(tools);

const agentNode = async (state: typeof AgentState.State) => {
  const response = await modelWithTools.invoke(state.messages);
  return { messages: [response] };
};

const toolNode = async (state: typeof AgentState.State) => {
  const lastMessage = state.messages.at(-1);
  if (!lastMessage || !AIMessage.isInstance(lastMessage)) {
    return { messages: [] };
  }

  const toolsByName = { [search.name]: search, [calculate.name]: calculate };
  const result = [];

  for (const toolCall of lastMessage.tool_calls ?? []) {
    const tool = toolsByName[toolCall.name];
    const observation = await tool.invoke(toolCall);
    result.push(observation);
  }

  return { messages: result };
};

const shouldContinue = (state: typeof AgentState.State) => {
  const lastMessage = state.messages.at(-1);
  if (lastMessage && AIMessage.isInstance(lastMessage) && lastMessage.tool_calls?.length) {
    return "tools";
  }
  return END;
};

// Dynamic agent: model decides when to stop
const agent = new StateGraph(AgentState)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue, ["tools", END])
  .addEdge("tools", "agent")
  .compile();
```
