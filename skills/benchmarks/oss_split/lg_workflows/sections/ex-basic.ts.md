Fixed path workflow:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const WorkflowState = new StateSchema({
  data: z.string(),
  validated: z.boolean(),
  processed: z.boolean(),
});

const validate = async (state: typeof WorkflowState.State) => {
  const isValid = state.data.length > 0;
  return { validated: isValid };
};

const process = async (state: typeof WorkflowState.State) => {
  return {
    data: state.data.toUpperCase(),
    processed: true,
  };
};

// Fixed workflow: validate -> process
const workflow = new StateGraph(WorkflowState)
  .addNode("validate", validate)
  .addNode("process", process)
  .addEdge(START, "validate")
  .addEdge("validate", "process")  // Always go to process
  .addEdge("process", END)
  .compile();

const result = await workflow.invoke({ data: "hello" });
console.log(result);  // { data: 'HELLO', validated: true, processed: true }
```
