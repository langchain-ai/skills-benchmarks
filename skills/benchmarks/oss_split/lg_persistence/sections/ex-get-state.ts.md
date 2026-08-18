Get current state and history:

```typescript
// Get current state
const config = { configurable: { thread_id: "conversation-1" } };
const currentState = await graph.getState(config);
console.log(currentState.values);  // Current state
console.log(currentState.next);    // Next nodes to execute

// Get state history
const history = await graph.getStateHistory(config);
for await (const state of history) {
  console.log("Step:", state.values);
}
```
