Thread-scoped memory with checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def respond(state):
    # Access conversation history
    history = state["messages"]
    return {"messages": [f"I remember {len(history)} messages"]}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("respond", respond)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)
)

# First turn
config = {"configurable": {"thread_id": "user-1"}}
graph.invoke({"messages": ["Hello"]}, config)

# Second turn - remembers first
graph.invoke({"messages": ["How are you?"]}, config)
# Response: "I remember 3 messages" (Hello, response, How are you?)
```
