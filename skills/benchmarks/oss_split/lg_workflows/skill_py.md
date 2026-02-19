---
name: LangGraph Workflows (Python)
description: "[LangGraph] Understanding workflows vs agents, predetermined vs dynamic patterns, and orchestrator-worker patterns using the Send API"
---

<overview>
LangGraph supports both **workflows** (predetermined paths) and **agents** (dynamic decision-making). Understanding when to use each pattern is crucial for effective agent design.

**Key Distinctions:**
- **Workflows**: Predetermined code paths, operate in specific order
- **Agents**: Dynamic, define their own processes and tool usage
- **Hybrid**: Combine deterministic and agentic steps
</overview>

<workflow-vs-agent>

| Characteristic | Workflow | Agent | Hybrid |
|----------------|----------|-------|--------|
| **Control Flow** | Fixed, predetermined | Dynamic, model-driven | Mixed |
| **Predictability** | High | Low | Medium |
| **Complexity** | Simple | Complex | Variable |
| **Use Case** | Sequential tasks | Open-ended problems | Structured flexibility |
| **Examples** | ETL, validation | Research, QA | Review approval |

</workflow-vs-agent>

<key-patterns>
### 1. Predetermined Workflows

Sequential execution with fixed paths:
- Data processing pipelines
- Validation workflows
- Multi-step transformations

### 2. Dynamic Agents

Model decides next steps:
- ReAct agents (reasoning + acting)
- Tool-calling loops
- Autonomous task completion

### 3. Orchestrator-Worker Pattern

One coordinator delegates to multiple workers:
- Map-reduce operations
- Parallel processing
- Multi-agent collaboration
</key-patterns>

<ex-basic-workflow>
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

# Fixed workflow: validate → process
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
</ex-basic-workflow>

<ex-dynamic-agent>
```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def calculate(a: float, b: float, op: str) -> str:
    """Perform a mathematical operation.

    Args:
        a: First number
        b: Second number
        op: Operation (add, subtract, multiply, divide)
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return str(ops.get(op, "Invalid operation"))

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

model = init_chat_model("claude-sonnet-4-5-20250929")
tools = [search, calculate]
model_with_tools = model.bind_tools(tools)

def agent_node(state: AgentState) -> dict:
    """Agent decides which tool to use (if any)."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute tools chosen by agent."""
    tools_by_name = {tool.name: tool for tool in tools}
    result = []

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: AgentState):
    """Dynamic: agent decides if it needs more tools."""
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# Dynamic agent: model decides when to stop
agent = (
    StateGraph(AgentState)
    .add_node("agent", agent_node)
    .add_node("tools", tool_node)
    .add_edge(START, "agent")
    .add_conditional_edges("agent", should_continue)  # Model decides
    .add_edge("tools", "agent")
    .compile()
)
```
</ex-dynamic-agent>

<ex-orchestrator-worker>
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
</ex-orchestrator-worker>

<ex-hybrid-workflow>
```python
class HybridState(TypedDict):
    input: str
    validated: bool
    agent_response: str
    finalized: bool

def validate(state: HybridState) -> dict:
    """Fixed validation step."""
    return {"validated": True}

def agent_process(state: HybridState) -> dict:
    """Dynamic: agent decides how to process."""
    # Agent logic here
    response = f"Agent processed: {state['input']}"
    return {"agent_response": response}

def finalize(state: HybridState) -> dict:
    """Fixed finalization step."""
    return {"finalized": True}

# Hybrid: validate → agent → finalize
hybrid = (
    StateGraph(HybridState)
    .add_node("validate", validate)      # Workflow
    .add_node("agent", agent_process)    # Agent
    .add_node("finalize", finalize)      # Workflow
    .add_edge(START, "validate")
    .add_edge("validate", "agent")
    .add_edge("agent", "finalize")
    .add_edge("finalize", END)
    .compile()
)
```
</ex-hybrid-workflow>

<ex-map-reduce>
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
</ex-map-reduce>

<ex-parallel-router>
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
</ex-parallel-router>

<boundaries>
### What You CAN Configure

- Choose workflow vs agent pattern
- Mix deterministic and agentic steps
- Use Send API for parallel execution
- Define custom orchestrator logic
- Control worker node behavior
- Aggregate results with reducers

### What You CANNOT Configure

- Change Send API message-passing model
- Bypass worker state isolation
- Modify parallel execution mechanism
- Override reducer behavior at runtime
</boundaries>

<fix-worker-state-isolation>
```python
# WRONG: WRONG - Workers share state, causing conflicts
class State(TypedDict):
    shared_counter: int  # All workers modify same counter!

# CORRECT: CORRECT - Each worker gets isolated input
def worker(state: dict) -> dict:
    # state is isolated to this worker
    return {"results": [process(state["task"])]}
```
</fix-worker-state-isolation>

<fix-send-accumulator>
```python
# WRONG: WRONG - Last worker overwrites all others
class State(TypedDict):
    results: list  # No reducer!

# CORRECT: CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates
```
</fix-send-accumulator>

<fix-workflow-flexibility>
```python
# WRONG: ANTI-PATTERN - Overly rigid workflow
# What if validation fails? No recovery path!
.add_edge("validate", "process")  # Always proceeds

# CORRECT: BETTER - Add conditional logic
def route_after_validate(state):
    if not state["validated"]:
        return "error_handler"
    return "process"

.add_conditional_edges("validate", route_after_validate)
```
</fix-workflow-flexibility>

<fix-agent-guardrails>
```python
# WRONG: RISKY - Pure agent, no guardrails
# Agent might loop forever or make bad choices

# CORRECT: BETTER - Hybrid with constraints
def should_continue(state):
    # Add max iterations check
    if state["iterations"] > 10:
        return END
    if state["messages"][-1].tool_calls:
        return "tools"
    return END
```
</fix-agent-guardrails>

<links>
- [Workflows and Agents (Python)](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Send API Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Map-Reduce Example](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
</links>
