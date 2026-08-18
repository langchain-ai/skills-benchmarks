Async node returning state update:

```typescript
const myNode = async (state: State): Promise<Partial<State>> => {
  // Nodes are just async functions!
  return { key: "updated_value" };
};
```
