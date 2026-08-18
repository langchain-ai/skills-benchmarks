Pause execution for human review using dynamic interrupt and resume with Command.
```typescript
import { interrupt, Command, MemorySaver, StateGraph, START, END } from "@langchain/langgraph";

const reviewNode = async (state: typeof State.State) => {
  if (state.needsReview) {
    const userResponse = interrupt({
      action: "review",
      data: state.draft,
      question: "Approve this draft?"
    });
    if (userResponse === "reject") {
      return { status: "rejected" };
    }
  }
  return { status: "approved" };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("review", reviewNode)
  .addEdge(START, "review")
  .addEdge("review", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "1" } };
let result = await graph.invoke({ needsReview: true, draft: "content" }, config);

// Check for interrupt
if (result.__interrupt__) {
  console.log(result.__interrupt__);
}

// Resume with user decision
result = await graph.invoke(new Command({ resume: "approve" }), config);
```
