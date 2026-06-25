Use defaults in schema:

```typescript
// RISKY - No default handling
const State = new StateSchema({
  count: z.number(),  // What if undefined?
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };  // May error if count undefined
};

// BETTER - Use defaults in schema
const State = new StateSchema({
  count: z.number().default(0),
});
```
