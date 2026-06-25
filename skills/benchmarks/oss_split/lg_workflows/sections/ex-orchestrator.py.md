Fan-out with Send API:

```python
from langgraph.types import Send
from typing import Annotated
import operator

class OrchestratorState(TypedDict):
    tasks: list[str]
    results: Annotated[list, operator.add]

def orchestrator(state: OrchestratorState):
    """Fan out tasks to workers."""
    return [
        Send("worker", {"task": task})
        for task in state["tasks"]
    ]

def worker(state: dict) -> dict:
    """Individual worker processes one task."""
    task = state["task"]
    result = f"Completed: {task}"
    return {"results": [result]}

def synthesize(state: OrchestratorState) -> dict:
    """Combine worker outputs."""
    summary = f"Processed {len(state['results'])} tasks"
    return {"summary": summary}

graph = (
    StateGraph(OrchestratorState)
    .add_node("worker", worker)
    .add_node("synthesize", synthesize)
    .add_conditional_edges(START, orchestrator, ["worker"])
    .add_edge("worker", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)

result = graph.invoke({
    "tasks": ["Task A", "Task B", "Task C"]
})
print(result["summary"])  # "Processed 3 tasks"
```
