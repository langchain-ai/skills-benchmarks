"""A data processing pipeline that fans out work to parallel workers.

Issues reported by users:
- "The pipeline crashes when I give it multiple tasks"
- "Even when it works, I only get one result back instead of all of them"
- "There's no way to review results before they're finalized"
- "When I try to resume after reviewing, it starts over from scratch"
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# BUG 1: No reducer on results - parallel workers crash
class PipelineState(TypedDict):
    tasks: list[str]
    results: list  # Should be Annotated[list, operator.add]
    summary: str
    status: str


def fan_out(state: PipelineState):
    """Distribute tasks to parallel workers."""
    # BUG 2: Only sends first task instead of all tasks
    return [Send("process_task", {"task": state["tasks"][0]})]


def process_task(state: dict) -> dict:
    """Process a single task."""
    task = state["task"]
    return {"results": [f"processed:{task}"]}


def review(state: PipelineState) -> dict:
    """Review results before finalizing."""
    # BUG 2: No interrupt - should pause for human review when many results
    return {"status": "approved"}


def summarize(state: PipelineState) -> dict:
    """Create final summary from approved results."""
    count = len(state.get("results", []))
    return {"summary": f"Pipeline complete: {count} tasks processed"}


# Build the pipeline
builder = StateGraph(PipelineState)
builder.add_node("process_task", process_task)
builder.add_node("review", review)
builder.add_node("summarize", summarize)
builder.add_conditional_edges(START, fan_out, ["process_task"])
builder.add_edge("process_task", "review")
builder.add_edge("review", "summarize")
builder.add_edge("summarize", END)

# BUG 3: No checkpointer - can't pause/resume for review
graph = builder.compile()


def run_pipeline(tasks: list[str], thread_id: str = "default") -> dict:
    """Run the data processing pipeline."""
    # BUG 4: No thread_id in config
    result = graph.invoke({
        "tasks": tasks,
        "results": [],
        "summary": "",
        "status": "",
    })
    return result


def resume_after_review(thread_id: str = "default") -> dict:
    """Resume pipeline after human review."""
    # BUG 5: Passes new input instead of Command(resume=...)
    result = graph.invoke({
        "tasks": [],
        "results": [],
        "summary": "",
        "status": "approved",
    })
    return result


if __name__ == "__main__":
    print("=== Data Processing Pipeline ===\n")

    # This will crash with InvalidUpdateError due to missing reducer
    try:
        result = run_pipeline(["task_a", "task_b", "task_c"])
        print(f"Results: {result.get('results')}")
        print(f"Summary: {result.get('summary')}")
    except Exception as e:
        print(f"ERROR: {e}")
