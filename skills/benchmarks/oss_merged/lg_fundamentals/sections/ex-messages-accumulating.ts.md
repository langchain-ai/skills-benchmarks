MessagesValue provides built-in accumulation for message arrays.
```typescript
import { StateSchema, MessagesValue, StateGraph, START, END } from "@langchain/langgraph";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

const State = new StateSchema({ messages: MessagesValue });

const addResponse = async (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  return { messages: [new AIMessage({ content: `Response to: ${lastMessage?.content}` })] };
};

// After invoke: messages list has BOTH original + response
```
