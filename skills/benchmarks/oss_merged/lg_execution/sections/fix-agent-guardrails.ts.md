Add max iterations check to prevent infinite loops.
```typescript
// RISKY: Might loop forever
const shouldContinue = (state) => state.messages.at(-1)?.tool_calls?.length ? "tools" : END;

// BETTER
const shouldContinue = (state) => {
  if (state.iterations > 10) return END;
  return state.messages.at(-1)?.tool_calls?.length ? "tools" : END;
};
```
