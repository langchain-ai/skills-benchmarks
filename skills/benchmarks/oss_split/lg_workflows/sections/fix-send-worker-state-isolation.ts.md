Workers receive isolated state:

```typescript
// WRONG - Workers share state, causing conflicts
const State = new StateSchema({
  sharedCounter: z.number(),  // All workers modify same counter!
});

// CORRECT - Each worker gets isolated input
const worker = async (state: { task: string }) => {
  // state is isolated to this worker
  return { results: [process(state.task)] };
};
```
