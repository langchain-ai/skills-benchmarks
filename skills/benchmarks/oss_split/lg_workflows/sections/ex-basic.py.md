Fixed path workflow:

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    data: str
    validated: bool
    processed: bool

def validate(state: WorkflowState) -> dict:
    """Validate input data."""
    is_valid = len(state["data"]) > 0
    return {"validated": is_valid}

def process(state: WorkflowState) -> dict:
    """Process validated data."""
    return {
        "data": state["data"].upper(),
        "processed": True
    }

# Fixed workflow: validate -> process
workflow = (
    StateGraph(WorkflowState)
    .add_node("validate", validate)
    .add_node("process", process)
    .add_edge(START, "validate")
    .add_edge("validate", "process")  # Always go to process
    .add_edge("process", END)
    .compile()
)

result = workflow.invoke({"data": "hello"})
print(result)  # {'data': 'HELLO', 'validated': True, 'processed': True}
```
