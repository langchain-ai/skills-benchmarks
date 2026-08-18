Parallel processing with aggregation:

```python
class MapReduceState(TypedDict):
    documents: list[str]
    summaries: Annotated[list, operator.add]
    final_summary: str

def map_documents(state: MapReduceState):
    """Map: send each document to a worker."""
    return [
        Send("summarize", {"doc": doc})
        for doc in state["documents"]
    ]

def summarize(state: dict) -> dict:
    """Worker: summarize one document."""
    doc = state["doc"]
    summary = f"Summary of: {doc[:50]}..."
    return {"summaries": [summary]}

def reduce(state: MapReduceState) -> dict:
    """Reduce: combine all summaries."""
    final = " | ".join(state["summaries"])
    return {"final_summary": final}

graph = (
    StateGraph(MapReduceState)
    .add_node("summarize", summarize)
    .add_node("reduce", reduce)
    .add_conditional_edges(START, map_documents, ["summarize"])
    .add_edge("summarize", "reduce")
    .add_edge("reduce", END)
    .compile()
)

result = graph.invoke({
    "documents": ["Doc 1 content...", "Doc 2 content...", "Doc 3 content..."]
})
```
