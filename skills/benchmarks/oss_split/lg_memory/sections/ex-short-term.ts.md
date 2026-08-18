Thread-scoped memory with checkpointer:

```typescript
import { MemorySaver, StateGraph, StateSchema, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  messages: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});

const respond = async (state: typeof State.State) => {
  // Access conversation history
  const history = state.messages;
  return { messages: [`I remember ${history.length} messages`] };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("respond", respond)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });

// First turn
const config = { configurable: { thread_id: "user-1" } };
await graph.invoke({ messages: ["Hello"] }, config);

// Second turn - remembers first
await graph.invoke({ messages: ["How are you?"] }, config);
// Response: "I remember 3 messages" (Hello, response, How are you?)
```
