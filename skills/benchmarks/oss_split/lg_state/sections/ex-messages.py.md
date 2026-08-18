Accumulate messages with operator.add:

```python
from typing import Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def add_response(state: MessagesState) -> dict:
    user_msg = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Response to: {user_msg}")]}

graph = (
    StateGraph(MessagesState)
    .add_node("respond", add_response)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile()
)

result = graph.invoke({
    "messages": [HumanMessage(content="Hello!")]
})
print(len(result["messages"]))  # 2 (original + response)
```
