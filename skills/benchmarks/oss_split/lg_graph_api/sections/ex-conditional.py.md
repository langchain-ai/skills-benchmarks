Router with conditional branching:

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    query: str
    route: str

def classify(state: State) -> dict:
    """Classify the query type."""
    if "weather" in state["query"].lower():
        return {"route": "weather"}
    return {"route": "general"}

def weather_node(state: State) -> dict:
    return {"result": "Sunny, 72°F"}

def general_node(state: State) -> dict:
    return {"result": "General response"}

# Router function
def route_query(state: State) -> Literal["weather", "general"]:
    """Decide which node to execute next."""
    return state["route"]

graph = (
    StateGraph(State)
    .add_node("classify", classify)
    .add_node("weather", weather_node)
    .add_node("general", general_node)
    .add_edge(START, "classify")
    # Conditional edge based on state
    .add_conditional_edges(
        "classify",
        route_query,
        ["weather", "general"]  # Possible destinations
    )
    .add_edge("weather", END)
    .add_edge("general", END)
    .compile()
)

result = graph.invoke({"query": "What's the weather?"})
```
