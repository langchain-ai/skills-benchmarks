In-memory checkpointer for development:

```typescript
import { MemorySaver, StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  messages: z.array(z.string()),
});

const addMessage = async (state: typeof State.State) => {
  return { messages: [...state.messages, "Bot response"] };
};

// Create checkpointer
const checkpointer = new MemorySaver();

// Compile with checkpointer
const graph = new StateGraph(State)
  .addNode("respond", addMessage)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });  // Enable persistence

// First invocation with thread_id
const config = { configurable: { thread_id: "conversation-1" } };
const result1 = await graph.invoke({ messages: ["Hello"] }, config);
console.log(result1.messages.length);  // 2

// Second invocation - state persisted
const result2 = await graph.invoke({ messages: ["How are you?"] }, config);
console.log(result2.messages.length);  // 4 (previous + new)
```
