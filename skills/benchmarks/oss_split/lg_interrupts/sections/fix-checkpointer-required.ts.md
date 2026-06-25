Enable persistence for interrupts:

```typescript
// WRONG - No checkpointer
const graph = builder.compile();  // No persistence!
await graph.invoke(...);  // Interrupt won't work

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
