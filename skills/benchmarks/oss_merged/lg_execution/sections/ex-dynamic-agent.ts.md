Build a ReAct agent that dynamically decides when to call tools based on model responses.
```typescript
import { tool } from "@langchain/core/tools";
import { ChatOpenAI } from "@langchain/openai";
import { ToolMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const searchTool = tool(
  async ({ query }) => `Results for: ${query}`,
  { name: "search", description: "Search for information", schema: z.object({ query: z.string() }) }
);

const State = new StateSchema({ messages: MessagesValue });

const model = new ChatOpenAI({ model: "gpt-4" });
const modelWithTools = model.bindTools([searchTool]);

const agentNode = async (state: typeof State.State) => {
  const response = await modelWithTools.invoke(state.messages);
  return { messages: [response] };
};

const toolNode = async (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  const results = [];
  for (const toolCall of lastMessage.tool_calls ?? []) {
    const observation = await searchTool.invoke(toolCall.args);
    results.push(new ToolMessage({ content: observation, tool_call_id: toolCall.id }));
  }
  return { messages: results };
};

const shouldContinue = (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  return lastMessage?.tool_calls?.length ? "tools" : END;
};

const agent = new StateGraph(State)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile();
```
