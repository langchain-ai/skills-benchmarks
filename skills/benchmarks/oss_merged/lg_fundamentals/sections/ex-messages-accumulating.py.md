Messages accumulate via reducer - new messages append, not overwrite.
```python
from typing import Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def add_response(state: MessagesState) -> dict:
    user_msg = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Response to: {user_msg}")]}

# After invoke: messages list has BOTH original + response (not overwritten)
```
