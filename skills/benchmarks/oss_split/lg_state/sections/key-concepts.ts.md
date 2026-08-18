Define state with StateSchema and Zod:

```typescript
import { StateSchema } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  input: z.string(),
  output: z.string(),
  count: z.number(),
});
```
