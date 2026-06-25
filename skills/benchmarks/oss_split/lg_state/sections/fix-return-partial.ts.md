Return partial updates only:

```typescript
// WRONG - Returning entire state object
const myNode = async (state: typeof State.State) => {
  state.field = "updated";
  return state;  // Don't do this!
};

// CORRECT - Return partial updates
const myNode = async (state: typeof State.State) => {
  return { field: "updated" };
};
```
