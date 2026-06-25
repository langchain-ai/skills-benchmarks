Use both memory types together:

```typescript
const smartNode = async (state, config) => {
  const store = config.store;

  // Short-term: conversation context
  const recentMessages = state.messages.slice(-5);  // Last 5 messages

  // Long-term: user profile
  const userId = state.userId;
  const profile = await store.get([userId, "profile"], "info");

  // Use both for personalized response
  const response = await generateResponse(recentMessages, profile);

  return { messages: [response] };
};

const graph = new StateGraph(State)
  .addNode("respond", smartNode)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer, store });
```
