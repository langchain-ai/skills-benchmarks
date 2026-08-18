Basic graph with static edges:

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# 1. Define state
class State(TypedDict):
    input: str
    output: str

# 2. Define nodes
def process_input(state: State) -> dict:
    return {"output": f"Processed: {state['input']}"}

def finalize(state: State) -> dict:
    return {"output": state["output"].upper()}

# 3. Build graph
graph = (
    StateGraph(State)
    .add_node("process", process_input)
    .add_node("finalize", finalize)
    .add_edge(START, "process")       # Entry point
    .add_edge("process", "finalize")  # Static edge
    .add_edge("finalize", END)        # Exit point
    .compile()
)

# 4. Execute
result = graph.invoke({"input": "hello"})
print(result["output"])  # "PROCESSED: HELLO"
```
