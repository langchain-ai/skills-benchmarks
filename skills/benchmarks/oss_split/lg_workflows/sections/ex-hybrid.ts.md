Mix deterministic and agentic steps:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const HybridState = new StateSchema({
  input: z.string(),
  validated: z.boolean(),
  agentResponse: z.string().optional(),
  finalized: z.boolean(),
});

const validate = async (state: typeof HybridState.State) => {
  return { validated: true };
};

const agentProcess = async (state: typeof HybridState.State) => {
  // Dynamic agent logic here
  const response = `Agent processed: ${state.input}`;
  return { agentResponse: response };
};

const finalize = async (state: typeof HybridState.State) => {
  return { finalized: true };
};

// Hybrid: validate -> agent -> finalize
const hybrid = new StateGraph(HybridState)
  .addNode("validate", validate)      // Workflow
  .addNode("agent", agentProcess)     // Agent
  .addNode("finalize", finalize)      // Workflow
  .addEdge(START, "validate")
  .addEdge("validate", "agent")
  .addEdge("agent", "finalize")
  .addEdge("finalize", END)
  .compile();
```
