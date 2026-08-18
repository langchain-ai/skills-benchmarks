Pause execution for human review using dynamic interrupt and resume with Command.
```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

def review_node(state):
    if state["needs_review"]:
        user_response = interrupt({
            "action": "review",
            "data": state["draft"],
            "question": "Approve this draft?"
        })
        if user_response == "reject":
            return {"status": "rejected"}
    return {"status": "approved"}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("review", review_node)
    .add_edge(START, "review")
    .add_edge("review", END)
    .compile(checkpointer=checkpointer)
)

config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"needs_review": True, "draft": "content"}, config)

# Check for interrupt
if "__interrupt__" in result:
    print(result["__interrupt__"])

# Resume with user decision
result = graph.invoke(Command(resume="approve"), config)
```
