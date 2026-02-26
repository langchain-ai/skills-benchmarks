"""A data processing pipeline — FIXED VERSION."""

import operator
from typing import Annotated

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send, interrupt
from typing_extensions import TypedDict


# FIX 1: Added reducer for parallel result accumulation
class PipelineState(TypedDict):
    tasks: list[str]
    results: Annotated[list, operator.add]
    summary: str
    status: str


# FIX 2: Fan out ALL tasks, not just the first
def fan_out(state: PipelineState):
    """Distribute tasks to parallel workers."""
    return [Send("process_task", {"task": task}) for task in state["tasks"]]


def process_task(state: dict) -> dict:
    """Process a single task."""
    task = state["task"]
    return {"results": [f"processed:{task}"]}


# FIX 3: Added interrupt for human review
def review(state: PipelineState) -> dict:
    """Review results before finalizing."""
    answer = interrupt({
        "question": "Approve these results?",
        "count": len(state.get("results", [])),
        "results": state.get("results", []),
    })
    if answer == "reject":
        return {"status": "rejected"}
    return {"status": "approved"}


def summarize(state: PipelineState) -> dict:
    """Create final summary from approved results."""
    count = len(state.get("results", []))
    return {"summary": f"Pipeline complete: {count} tasks processed"}


builder = StateGraph(PipelineState)
builder.add_node("process_task", process_task)
builder.add_node("review", review)
builder.add_node("summarize", summarize)
builder.add_conditional_edges(START, fan_out, ["process_task"])
builder.add_edge("process_task", "review")
builder.add_edge("review", "summarize")
builder.add_edge("summarize", END)

# FIX 4: Added checkpointer for interrupt/resume
graph = builder.compile(checkpointer=MemorySaver())


# FIX 5: Added thread_id config
def run_pipeline(tasks: list[str], thread_id: str = "default") -> dict:
    """Run the data processing pipeline."""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {
            "tasks": tasks,
            "results": [],
            "summary": "",
            "status": "",
        },
        config,
    )
    return result


# FIX 6: Use Command(resume=...) instead of new input
def resume_after_review(thread_id: str = "default") -> dict:
    """Resume pipeline after human review."""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(Command(resume="approve"), config)
    return result
