Accumulate messages with MessagesValue:

```typescript
import { StateSchema, MessagesValue, StateGraph, START, END } from "@langchain/langgraph";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

const MessagesState = new StateSchema({
  messages: MessagesValue,
});

const addResponse = async (state: typeof MessagesState.State) => {
  const lastMessage = state.messages.at(-1);
  const userMsg = lastMessage?.content || "";
  return {
    messages: [new AIMessage({ content: `Response to: ${userMsg}` })],
  };
};

const graph = new StateGraph(MessagesState)
  .addNode("respond", addResponse)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile();

const result = await graph.invoke({
  messages: [new HumanMessage({ content: "Hello!" })],
});
console.log(result.messages.length);  // 2 (original + response)
```
