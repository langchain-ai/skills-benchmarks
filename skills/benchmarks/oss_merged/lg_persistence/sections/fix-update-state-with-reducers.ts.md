Use Overwrite to replace state values instead of passing through reducers.
```typescript
import { Overwrite } from "@langchain/langgraph";

// State with reducer: items uses concat reducer
// Current state: { items: ["A", "B"] }

// updateState PASSES THROUGH reducers
await graph.updateState(config, { items: ["C"] });  // Result: ["A", "B", "C"] - Appended!

// To REPLACE instead, use Overwrite
await graph.updateState(config, { items: new Overwrite(["C"]) });  // Result: ["C"] - Replaced
```
