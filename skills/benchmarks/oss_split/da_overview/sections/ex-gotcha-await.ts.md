Always await the async function:

```typescript
// Missing await
const agent = createDeepAgent({});

// createDeepAgent is async
const agent = await createDeepAgent({});
```
