In-memory checkpointer for development:

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def add_message(state: State) -> dict:
    return {"messages": ["Bot response"]}

# Create checkpointer
checkpointer = InMemorySaver()

# Compile with checkpointer
graph = (
    StateGraph(State)
    .add_node("respond", add_message)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)  # Enable persistence
)

# First invocation with thread_id
config = {"configurable": {"thread_id": "conversation-1"}}
result1 = graph.invoke({"messages": ["Hello"]}, config)
print(len(result1["messages"]))  # 2

# Second invocation - state persisted
result2 = graph.invoke({"messages": ["How are you?"]}, config)
print(len(result2["messages"]))  # 4 (previous + new)
```
