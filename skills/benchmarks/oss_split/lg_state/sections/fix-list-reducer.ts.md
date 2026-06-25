Add ReducedValue for array accumulation:

```typescript
// WRONG - Array will be overwritten
const State = new StateSchema({
  items: z.array(z.string()),  // No reducer!
});

// Node 1 returns: { items: ["A"] }
// Node 2 returns: { items: ["B"] }
// Final state: { items: ["B"] }  // A is lost!

// CORRECT
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
// Final state: { items: ["A", "B"] }
```
