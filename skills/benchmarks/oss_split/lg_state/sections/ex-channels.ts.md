Low-level channel configuration:

```typescript
import { StateGraph, LastValue, BinaryOperatorAggregate } from "@langchain/langgraph";

interface State {
  counter: number;
  logs: string[];
}

const graph = new StateGraph<State>({
  channels: {
    counter: new BinaryOperatorAggregate<number>(
      (x, y) => x + y,
      () => 0
    ),
    logs: new BinaryOperatorAggregate<string[]>(
      (x, y) => x.concat(y),
      () => []
    ),
  },
});
```
