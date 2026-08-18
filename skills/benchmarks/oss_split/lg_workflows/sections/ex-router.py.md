Route to multiple sources:

```python
from langgraph.types import Send

class RouterState(TypedDict):
    query: str
    sources: list[str]
    results: Annotated[list, operator.add]

def classify(state: RouterState) -> dict:
    """Determine which sources to query."""
    query = state["query"].lower()
    sources = []

    if "code" in query:
        sources.append("github")
    if "doc" in query:
        sources.append("notion")
    if "message" in query:
        sources.append("slack")

    return {"sources": sources}

def route_to_sources(state: RouterState):
    """Fan out to relevant sources."""
    return [
        Send(source, {"query": state["query"]})
        for source in state["sources"]
    ]

def query_github(state: dict) -> dict:
    return {"results": [f"GitHub: {state['query']}"]}

def query_notion(state: dict) -> dict:
    return {"results": [f"Notion: {state['query']}"]}

def query_slack(state: dict) -> dict:
    return {"results": [f"Slack: {state['query']}"]}

def synthesize(state: RouterState) -> dict:
    return {"final": " + ".join(state["results"])}

graph = (
    StateGraph(RouterState)
    .add_node("classify", classify)
    .add_node("github", query_github)
    .add_node("notion", query_notion)
    .add_node("slack", query_slack)
    .add_node("synthesize", synthesize)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_sources)
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)
```
