Interrupts occur between invoke calls:

```typescript
// Interrupts happen between invoke() calls

// Step 1: invoke() -> interrupt
await agent.invoke({...}, config);

// Step 2: Check state
const state = await agent.getState(config);
if (state.next) {
  // Handle interrupts
}

// Step 3: Resume
await agent.updateState(config, {...});
await agent.invoke(null, config);
```
