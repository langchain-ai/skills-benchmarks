Add checkpointer for short-term memory:

```typescript
// WRONG - No checkpointer, no memory
const graph = builder.compile();  // Messages lost!

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
