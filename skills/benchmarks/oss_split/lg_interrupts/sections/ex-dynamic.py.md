Pause for human review:

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

def review_node(state):
    # Conditionally pause for review
    if state["needs_review"]:
        # Pause and surface data to user
        user_response = interrupt({
            "action": "review",
            "data": state["draft"],
            "question": "Approve this draft?"
        })

        # user_response comes from Command(resume=...)
        if user_response == "reject":
            return {"status": "rejected"}

    return {"status": "approved"}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("review", review_node)
    .add_edge(START, "review")
    .add_edge("review", END)
    .compile(checkpointer=checkpointer)  # Required!
)

# Initial invocation - will pause
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"needs_review": True, "draft": "content"}, config)

# Check for interrupt
if "__interrupt__" in result:
    print(result["__interrupt__"])  # See interrupt payload

# Resume with user decision
from langgraph.types import Command
result = graph.invoke(
    Command(resume="approve"),  # User's response
    config
)
```
