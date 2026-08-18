Pause for human review:

```typescript
import { interrupt, Command } from "@langchain/langgraph";
import { MemorySaver } from "@langchain/langgraph";

const reviewNode = async (state) => {
  // Conditionally pause for review
  if (state.needsReview) {
    // Pause and surface data to user
    const userResponse = interrupt({
      action: "review",
      data: state.draft,
      question: "Approve this draft?",
    });

    // userResponse comes from Command({ resume: ... })
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
  .compile({ checkpointer });  // Required!

// Initial invocation - will pause
const config = { configurable: { thread_id: "1" } };
const result = await graph.invoke(
  { needsReview: true, draft: "content" },
  config
);

// Check for interrupt
if ("__interrupt__" in result) {
  console.log(result.__interrupt__);  // See interrupt payload
}

// Resume with user decision
const finalResult = await graph.invoke(
  new Command({ resume: "approve" }),  // User's response
  config
);
```
