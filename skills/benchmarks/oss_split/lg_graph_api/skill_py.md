---
name: LangGraph Graph API (Python)
description: "[LangGraph] Building graphs with StateGraph, nodes, edges, START/END nodes, and the Command API for combining control flow with state updates"
---

<overview>
The LangGraph Graph API allows you to define agent workflows as directed graphs composed of **nodes** (functions) and **edges** (control flow). This provides fine-grained control over agent orchestration.

**Core Components:**
- **StateGraph**: Main class for building stateful graphs
- **Nodes**: Functions that perform work and update state
- **Edges**: Define execution order (static or conditional)
- **START/END**: Special nodes marking graph entry and exit points
- **Command**: Combine state updates with dynamic routing
</overview>

<edge-type-selection>

| Need | Edge Type | When to Use |
|------|-----------|-------------|
| Always go to same node | `add_edge()` | Fixed, deterministic flow |
| Route based on state | `add_conditional_edges()` | Dynamic branching logic |
| Fan-out to multiple nodes | `Send` API | Map-reduce, parallel execution |
| Update state AND route | `Command` | Combine logic in single node |

</edge-type-selection>

<key-concepts>
### 1. Graph Execution Model

LangGraph uses a **message-passing** model inspired by Google's Pregel:
- Execution proceeds in **super-steps** (discrete iterations)
- Nodes in parallel are part of the same super-step
- Sequential nodes belong to separate super-steps
- Graph ends when all nodes are inactive and no messages in transit

### 2. Nodes

**Nodes** are Python functions that:
- Receive the current state as input
- Perform computation or side effects
- Return state updates (partial or full)

```python
def my_node(state: State) -> dict:
    """Nodes are just functions!"""
    return {"key": "updated_value"}
```

### 3. Edges

| Edge Type | Description | Example |
|-----------|-------------|---------|
| **Static** | Always routes to same node | `add_edge("A", "B")` |
| **Conditional** | Routes based on state/logic | `add_conditional_edges("A", router)` |
| **Dynamic (Send)** | Fan-out to multiple nodes | `Send("worker", {...})` |
| **Command** | State update + routing | `return Command(goto="B")` |

### 4. Special Nodes

- **START**: Entry point of the graph (virtual node)
- **END**: Terminal node (graph halts)
</key-concepts>

<ex-basic-graph>
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
</ex-basic-graph>

<ex-conditional-edges>
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
</ex-conditional-edges>

<ex-command-state-routing>
```python
from langgraph.types import Command
from typing import Literal

class State(TypedDict):
    count: int
    result: str

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    """Update state AND decide next node."""
    new_count = state["count"] + 1

    if new_count > 5:
        # Go to node_c
        return Command(
            update={"count": new_count, "result": "Going to C"},
            goto="node_c"
        )
    else:
        # Go to node_b
        return Command(
            update={"count": new_count, "result": "Going to B"},
            goto="node_b"
        )

def node_b(state: State) -> dict:
    return {"result": f"B executed, count={state['count']}"}

def node_c(state: State) -> dict:
    return {"result": f"C executed, count={state['count']}"}

graph = (
    StateGraph(State)
    .add_node("node_a", node_a)
    .add_node("node_b", node_b)
    .add_node("node_c", node_c)
    .add_edge(START, "node_a")
    .add_edge("node_b", END)
    .add_edge("node_c", END)
    .compile()
)

result = graph.invoke({"count": 0})
print(result["result"])  # "B executed, count=1"

result = graph.invoke({"count": 5})
print(result["result"])  # "C executed, count=6"
```
</ex-command-state-routing>

<ex-map-reduce-send>
```python
from langgraph.types import Send
from typing import Annotated
import operator

class State(TypedDict):
    items: list[str]
    results: Annotated[list, operator.add]  # Accumulate results

def fan_out(state: State):
    """Send each item to a worker node."""
    return [
        Send("worker", {"item": item})
        for item in state["items"]
    ]

def worker(state: dict) -> dict:
    """Process a single item."""
    item = state["item"]
    return {"results": [f"Processed: {item}"]}

def aggregate(state: State) -> dict:
    """Combine results."""
    return {"final": ", ".join(state["results"])}

graph = (
    StateGraph(State)
    .add_node("worker", worker)
    .add_node("aggregate", aggregate)
    .add_conditional_edges(START, fan_out, ["worker"])
    .add_edge("worker", "aggregate")
    .add_edge("aggregate", END)
    .compile()
)

result = graph.invoke({"items": ["A", "B", "C"]})
print(result["final"])  # "Processed: A, Processed: B, Processed: C"
```
</ex-map-reduce-send>

<ex-graph-with-loops>
```python
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    count: int
    max_iterations: int

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}

def should_continue(state: State) -> str:
    """Loop until max iterations reached."""
    if state["count"] >= state["max_iterations"]:
        return END
    return "increment"

graph = (
    StateGraph(State)
    .add_node("increment", increment)
    .add_edge(START, "increment")
    .add_conditional_edges("increment", should_continue)
    .compile()
)

result = graph.invoke({"count": 0, "max_iterations": 5})
print(result["count"])  # 5
```
</ex-graph-with-loops>

<ex-compile-options>
```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("node_a", node_a)
    .add_edge(START, "node_a")
    .add_edge("node_a", END)
    .compile(
        checkpointer=checkpointer,      # Enable persistence
        interrupt_before=["node_a"],    # Breakpoint before node
        interrupt_after=["node_a"],     # Breakpoint after node
    )
)
```
</ex-compile-options>

<boundaries>
### What Agents CAN Configure

- Define custom nodes (any Python function)
- Add static edges between nodes
- Add conditional edges with custom logic
- Use Command for combined state/routing
- Create loops with conditional termination
- Fan-out with Send API (map-reduce)
- Set breakpoints (interrupt_before/after)
- Customize state schema
- Specify checkpointer for persistence

### What Agents CANNOT Configure

- Modify START/END node behavior
- Change super-step execution model
- Alter message-passing protocol
- Override graph compilation logic
- Bypass state update mechanism
</boundaries>

<fix-compile-before-execution>
```python
# WRONG: WRONG
builder = StateGraph(State).add_node("node", func)
builder.invoke({"input": "test"})  # AttributeError!

# CORRECT: CORRECT
graph = builder.compile()
graph.invoke({"input": "test"})
```
</fix-compile-before-execution>

<fix-conditional-edge-destinations>
```python
# WRONG: WRONG - "missing_node" not added to graph
def router(state):
    return "missing_node"

builder.add_conditional_edges("node_a", router, ["missing_node"])

# CORRECT: CORRECT - Add all possible destinations
builder.add_node("missing_node", func)
builder.add_conditional_edges("node_a", router, ["missing_node"])
```
</fix-conditional-edge-destinations>

<fix-command-type-annotation>
```python
# WRONG: WRONG - No type hint for routing
def node_a(state) -> Command:
    return Command(goto="node_b")

# CORRECT: CORRECT - Specify possible destinations
from typing import Literal

def node_a(state) -> Command[Literal["node_b", "node_c"]]:
    return Command(goto="node_b")
```
</fix-command-type-annotation>

<fix-loop-exit-condition>
```python
# WRONG: WRONG - Infinite loop
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # No way out!

# CORRECT: CORRECT - Conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
</fix-loop-exit-condition>

<fix-send-api-accumulator>
```python
# WRONG: WRONG - Results will be overwritten
class State(TypedDict):
    results: list  # No reducer!

# CORRECT: CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates results
```
</fix-send-api-accumulator>

<fix-start-not-destination>
```python
# WRONG: WRONG - Cannot route back to START
builder.add_edge("node_a", START)  # Error!

# CORRECT: CORRECT - Use named entry node instead
builder.add_node("entry", entry_func)
builder.add_edge(START, "entry")
builder.add_edge("node_a", "entry")  # OK
```
</fix-start-not-destination>

<links>
- [Graph API Reference (Python)](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Using the Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [Command Documentation](https://docs.langchain.com/oss/python/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)
- [Send API Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Conditional Branching](https://docs.langchain.com/oss/python/langgraph/use-graph-api#conditional-branching)
</links>
