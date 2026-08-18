Checkpointer required for interrupt functionality.
```typescript
// WRONG
const graph = builder.compile();

// CORRECT
const graph = builder.compile({ checkpointer: new MemorySaver() });
```
