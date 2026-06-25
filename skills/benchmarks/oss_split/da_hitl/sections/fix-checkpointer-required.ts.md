Provide checkpointer for interrupt state:

```typescript
// Error
await createDeepAgent({ interruptOn: { write_file: true } });

// Must provide checkpointer
await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
