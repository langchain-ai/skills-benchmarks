---
name: LangGraph Fundamentals (Python)
description: "INVOKE THIS SKILL when writing ANY LangGraph code. Covers StateGraph creation, node functions, edges, state schemas with reducers (Annotated), and the Command API. CRITICAL: Contains fixes for returning partial state updates (not full state), missing reducers, and mutable defaults."
---

<overview>
LangGraph models agent workflows as **directed graphs**:

- **StateGraph**: Main class for building stateful graphs
- **Nodes**: Functions that perform work and update state
- **Edges**: Define execution order (static or conditional)
- **START/END**: Special nodes marking entry and exit points
- **State with Reducers**: Control how state updates are merged

Graphs must be `compile()`d before execution.
</overview>

<when-to-use-langgraph>

| Use LangGraph When | Use Alternatives When |
|-------------------|----------------------|
| Need fine-grained control over agent orchestration | Quick prototyping → LangChain agents |
| Building complex workflows with branching/loops | Simple stateless workflows → LCEL |
| Require human-in-the-loop, persistence | Batteries-included features → Deep Agents |
| Production deployment with durable execution | |

</when-to-use-langgraph>

---

## State Management

<state-update-strategies>

| Need | Solution | Example |
|------|----------|---------|
| Overwrite value | No reducer (default) | Simple fields like counters |
| Append to list | `Annotated[list, operator.add]` | Message history, logs |
| Custom logic | Custom reducer function | Complex merging |

</state-update-strategies>

<ex-state-with-reducer>
```python
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    # Default: overwrites on update
    name: str
    count: int

    # Reducer: appends to list (critical for messages!)
    messages: Annotated[list, operator.add]

    # Reducer: sums integers
    total: Annotated[int, operator.add]
```
</ex-state-with-reducer>

<ex-messages-accumulating>
```python
from typing import Annotated
import operator
from langchain.messages import BaseMessage, HumanMessage, AIMessage

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def add_response(state: MessagesState) -> dict:
    user_msg = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Response to: {user_msg}")]}

# After invoke: messages list has BOTH original + response (not overwritten)
```
</ex-messages-accumulating>

<fix-forgot-reducer-for-list>
```python
# WRONG: List will be OVERWRITTEN, not appended
class State(TypedDict):
    messages: list  # No reducer!

# Node 1 returns: {"messages": ["A"]}
# Node 2 returns: {"messages": ["B"]}
# Final state: {"messages": ["B"]}  # "A" is LOST!

# CORRECT: Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]
# Final state: {"messages": ["A", "B"]}  # Both preserved
```
</fix-forgot-reducer-for-list>

<fix-state-must-return-dict>
```python
# WRONG: Returning entire state object
def my_node(state: State) -> State:
    state["field"] = "updated"
    return state  # Don't mutate and return!

# CORRECT: Return dict with only the updates
def my_node(state: State) -> dict:
    return {"field": "updated"}
```
</fix-state-must-return-dict>

<fix-reducer-type-mismatch>
```python
# WRONG: Reducer expects list, but receives string
class State(TypedDict):
    items: Annotated[list, operator.add]

def bad_update(state: State) -> dict:
    return {"items": "not a list"}  # Type error!

# CORRECT: Return the correct type
def good_update(state: State) -> dict:
    return {"items": ["item"]}
```
</fix-reducer-type-mismatch>

---

## Building Graphs

<edge-type-selection>

| Need | Edge Type | When to Use |
|------|-----------|-------------|
| Always go to same node | `add_edge()` | Fixed, deterministic flow |
| Route based on state | `add_conditional_edges()` | Dynamic branching |
| Update state AND route | `Command` | Combine logic in single node |
| Fan-out to multiple nodes | `Send` API | Map-reduce, parallel execution |

</edge-type-selection>

<ex-basic-graph>
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str

def process_input(state: State) -> dict:
    return {"output": f"Processed: {state['input']}"}

def finalize(state: State) -> dict:
    return {"output": state["output"].upper()}

# Build graph
graph = (
    StateGraph(State)
    .add_node("process", process_input)
    .add_node("finalize", finalize)
    .add_edge(START, "process")       # Entry point
    .add_edge("process", "finalize")  # Static edge
    .add_edge("finalize", END)        # Exit point
    .compile()                        # MUST compile before use
)

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
    if "weather" in state["query"].lower():
        return {"route": "weather"}
    return {"route": "general"}

def weather_node(state: State) -> dict:
    return {"result": "Sunny, 72°F"}

def general_node(state: State) -> dict:
    return {"result": "General response"}

# Router function returns name of next node
def route_query(state: State) -> Literal["weather", "general"]:
    return state["route"]

graph = (
    StateGraph(State)
    .add_node("classify", classify)
    .add_node("weather", weather_node)
    .add_node("general", general_node)
    .add_edge(START, "classify")
    .add_conditional_edges(
        "classify",
        route_query,
        ["weather", "general"]  # Possible destinations
    )
    .add_edge("weather", END)
    .add_edge("general", END)
    .compile()
)
```
</ex-conditional-edges>

<ex-command-state-and-routing>
```python
from langgraph.types import Command
from typing import Literal

class State(TypedDict):
    count: int
    result: str

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    """Update state AND decide next node in one return."""
    new_count = state["count"] + 1

    if new_count > 5:
        return Command(
            update={"count": new_count, "result": "Going to C"},
            goto="node_c"
        )
    else:
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
```
</ex-command-state-and-routing>

<ex-graph-with-loop>
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
</ex-graph-with-loop>

<ex-map-reduce-with-send>
```python
from langgraph.types import Send
from typing import Annotated
import operator

class State(TypedDict):
    items: list[str]
    results: Annotated[list, operator.add]  # Accumulate results

def fan_out(state: State):
    """Send each item to a worker node."""
    return [Send("worker", {"item": item}) for item in state["items"]]

def worker(state: dict) -> dict:
    return {"results": [f"Processed: {state['item']}"]}

def aggregate(state: State) -> dict:
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
```
</ex-map-reduce-with-send>

<fix-compile-before-execution>
```python
# WRONG: StateGraph is not executable
builder = StateGraph(State).add_node("node", func)
builder.invoke({"input": "test"})  # AttributeError!

# CORRECT: Must compile first
graph = builder.compile()
graph.invoke({"input": "test"})
```
</fix-compile-before-execution>

<fix-infinite-loop-needs-exit>
```python
# WRONG: Infinite loop - no way to reach END
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # Loops forever!

# CORRECT: Conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
</fix-infinite-loop-needs-exit>

<fix-conditional-edge-destinations>
```python
# WRONG: Router returns node that doesn't exist
def router(state):
    return "missing_node"

builder.add_conditional_edges("node_a", router, ["missing_node"])
# Error: missing_node not added to graph!

# CORRECT: Add all destination nodes first
builder.add_node("missing_node", func)
builder.add_conditional_edges("node_a", router, ["missing_node"])
```
</fix-conditional-edge-destinations>

<fix-command-type-annotation>
```python
# WRONG: No type hint for routing destinations
def node_a(state) -> Command:
    return Command(goto="node_b")

# CORRECT: Specify possible destinations
from typing import Literal

def node_a(state) -> Command[Literal["node_b", "node_c"]]:
    return Command(goto="node_b")
```
</fix-command-type-annotation>

<fix-start-not-destination>
```python
# WRONG: Cannot route back to START
builder.add_edge("node_a", START)  # Error!

# CORRECT: Use a named entry node instead
builder.add_node("entry", entry_func)
builder.add_edge(START, "entry")
builder.add_edge("node_a", "entry")  # Loop back to entry, not START
```
</fix-start-not-destination>

<boundaries>
### What You CAN Configure

- Define custom state schemas with TypedDict
- Add reducers to control how state updates are merged
- Create nodes (any Python function)
- Add static and conditional edges
- Use Command for combined state/routing
- Create loops with conditional termination
- Fan-out with Send API (map-reduce)

### What You CANNOT Configure

- Modify START/END behavior
- Change the Pregel execution model
- Access state outside node functions
- Modify state directly (must return updates)
</boundaries>
