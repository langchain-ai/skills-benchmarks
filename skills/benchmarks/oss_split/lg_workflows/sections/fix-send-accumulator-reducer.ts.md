Use ReducedValue to collect results:

```typescript
// WRONG - Last worker overwrites all others
const State = new StateSchema({
  results: z.array(z.string()),  // No reducer!
});

// CORRECT - Use ReducedValue
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
```
