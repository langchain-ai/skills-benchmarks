Enable state persistence with checkpointer:

```typescript
import { MemorySaver } from "@langchain/langgraph";

// Create checkpointer for state persistence
const checkpointer = new MemorySaver();

// Compile with checkpointer
const agent = new StateGraph(MessagesState)
  .addNode("llmCall", llmCall)
  .addNode("toolNode", toolNode)
  .addEdge(START, "llmCall")
  .addConditionalEdges("llmCall", shouldContinue, ["toolNode", END])
  .addEdge("toolNode", "llmCall")
  .compile({ checkpointer });  // Add checkpointer

// First conversation turn
const config = { configurable: { thread_id: "1" } };
await agent.invoke(
  { messages: [new HumanMessage("Hi, I'm Alice")] },
  config
);

// Second turn - agent remembers context
await agent.invoke(
  { messages: [new HumanMessage("What's my name?")] },
  config
);
```
