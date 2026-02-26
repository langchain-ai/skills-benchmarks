---
name: LangGraph State (Python)
description: "[LangGraph] Managing state in LangGraph: schemas, reducers, channels, and message passing for coordinating agent execution"
---

<overview>
State is the central data structure in LangGraph that persists throughout graph execution. Proper state management is crucial for building reliable agents.

**Key Concepts:**
- **State Schema**: Defines the structure and types of your state
- **Reducers**: Control how state updates are applied
- **Channels**: Low-level state management primitives
- **Message Passing**: How nodes communicate via state updates
</overview>

<state-update-strategies>

| Need | Solution | Use Case |
|------|----------|----------|
| Overwrite value | No reducer (default) | Simple fields like counters |
| Append to list | `operator.add` | Message history, logs |
| Custom logic | Custom reducer | Complex merging, validation |
| Messages | `Annotated[list, add_messages]` | Chat applications |

</state-update-strategies>

<key-concepts>
### 1. State Schema with TypedDict

```python
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str
    count: int
```

### 2. Reducers

Reducers determine how updates are merged with existing state:

```python
from typing import Annotated
import operator

class State(TypedDict):
    # Default: overwrites
    name: str

    # Reducer: appends to list
    messages: Annotated[list, operator.add]

    # Reducer: sums integers
    total: Annotated[int, operator.add]
```

### 3. Channels API

For advanced state control:

| Channel Type | Behavior |
|-------------|----------|
| `LastValue` | Stores most recent value |
| `BinaryOperatorAggregate` | Combines with reducer |
| `Topic` | Collects all values |
| `EphemeralValue` | Resets between supersteps |

</key-concepts>

<ex-basic-state-management>
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    processed: str
    count: int

def process(state: State) -> dict:
    return {
        "processed": state["input"].upper(),
        "count": state.get("count", 0) + 1
    }

graph = (
    StateGraph(State)
    .add_node("process", process)
    .add_edge(START, "process")
    .add_edge("process", END)
    .compile()
)

result = graph.invoke({"input": "hello", "count": 0})
print(result)  # {'input': 'hello', 'processed': 'HELLO', 'count': 1}
```
</ex-basic-state-management>

<ex-messages-with-reducer>
```python
from typing import Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def add_response(state: MessagesState) -> dict:
    user_msg = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Response to: {user_msg}")]}

graph = (
    StateGraph(MessagesState)
    .add_node("respond", add_response)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile()
)

result = graph.invoke({
    "messages": [HumanMessage(content="Hello!")]
})
print(len(result["messages"]))  # 2 (original + response)
```
</ex-messages-with-reducer>

<ex-custom-reducer>
```python
from typing import Annotated

def merge_dicts(current: dict, update: dict) -> dict:
    """Custom reducer to merge dictionaries."""
    return {**current, **update}

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]
    data: str

def update_metadata(state: State) -> dict:
    return {"metadata": {"timestamp": "2024-01-01"}}

graph = (
    StateGraph(State)
    .add_node("update", update_metadata)
    .add_edge(START, "update")
    .add_edge("update", END)
    .compile()
)

result = graph.invoke({
    "metadata": {"user": "alice"},
    "data": "test"
})
# metadata is merged: {"user": "alice", "timestamp": "2024-01-01"}
```
</ex-custom-reducer>

<ex-bypassing-reducers-with-overwrite>
```python
from langgraph.types import Overwrite

class State(TypedDict):
    items: Annotated[list, operator.add]  # Has reducer

def reset_items(state: State) -> dict:
    # Bypass reducer and replace entire list
    return {"items": Overwrite(["new_item"])}

graph = (
    StateGraph(State)
    .add_node("reset", reset_items)
    .add_edge(START, "reset")
    .add_edge("reset", END)
    .compile()
)

result = graph.invoke({"items": ["old1", "old2"]})
print(result["items"])  # ['new_item'] (not appended)
```
</ex-bypassing-reducers-with-overwrite>

<ex-using-channels-api>
```python
from langgraph.channels import LastValue, BinaryOperatorAggregate

class State(TypedDict):
    counter: int
    logs: list[str]

# Alternative way to define state
from langgraph.graph import StateGraph

channels = {
    "counter": BinaryOperatorAggregate(int, operator.add, default=lambda: 0),
    "logs": BinaryOperatorAggregate(list, operator.add, default=lambda: [])
}

def increment(state: dict) -> dict:
    return {"counter": 1, "logs": ["incremented"]}

graph = (
    StateGraph(State, channels=channels)
    .add_node("increment", increment)
    .add_edge(START, "increment")
    .add_edge("increment", END)
    .compile()
)
```
</ex-using-channels-api>

<ex-partial-state-updates>
```python
class State(TypedDict):
    field1: str
    field2: str
    field3: str

def update_field1(state: State) -> dict:
    # Only update field1, others unchanged
    return {"field1": "updated"}

def update_field2(state: State) -> dict:
    # Only update field2
    return {"field2": "also updated"}

graph = (
    StateGraph(State)
    .add_node("node1", update_field1)
    .add_node("node2", update_field2)
    .add_edge(START, "node1")
    .add_edge("node1", "node2")
    .add_edge("node2", END)
    .compile()
)

result = graph.invoke({
    "field1": "original1",
    "field2": "original2",
    "field3": "original3"
})
# field1: "updated", field2: "also updated", field3: "original3"
```
</ex-partial-state-updates>

<boundaries>
### What You CAN Configure

- Define custom state schemas
- Add reducers to fields
- Create custom reducer functions
- Use built-in channels
- Bypass reducers with Overwrite
- Partial state updates
- Nested state structures

### What You CANNOT Configure

- Change state after graph compilation
- Access state outside node functions
- Modify state directly (must return updates)
- Share state between separate graphs
</boundaries>

<fix-forgot-reducer-for-list>
```python
# WRONG: WRONG - List will be overwritten
class State(TypedDict):
    items: list  # No reducer!

# Node 1 returns: {"items": ["A"]}
# Node 2 returns: {"items": ["B"]}
# Final state: {"items": ["B"]}  # A is lost!

# CORRECT: CORRECT
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]
# Final state: {"items": ["A", "B"]}
```
</fix-forgot-reducer-for-list>

<fix-state-must-return-dict>
```python
# WRONG: WRONG - Returning entire state object
def my_node(state: State) -> State:
    state["field"] = "updated"
    return state  # Don't do this!

# CORRECT: CORRECT - Return dict with updates
def my_node(state: State) -> dict:
    return {"field": "updated"}
```
</fix-state-must-return-dict>

<fix-default-values>
```python
# WRONG: RISKY - No default, may cause errors
class State(TypedDict):
    count: int  # What if not initialized?

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}  # KeyError!

# CORRECT: BETTER - Use .get() with default
def increment(state: State) -> dict:
    return {"count": state.get("count", 0) + 1}
```
</fix-default-values>

<fix-reducer-type-mismatch>
```python
# WRONG: WRONG - Reducer expects list, but receives string
class State(TypedDict):
    items: Annotated[list, operator.add]

def bad_update(state: State) -> dict:
    return {"items": "not a list"}  # Type error!

# CORRECT: CORRECT
def good_update(state: State) -> dict:
    return {"items": ["item"]}
```
</fix-reducer-type-mismatch>

<links>
- [State Management Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#process-state-updates-with-reducers)
- [Channels API](https://docs.langchain.com/oss/python/langgraph/use-graph-api#channels-api)
- [Schema Reference](https://docs.langchain.com/oss/python/langgraph/graph-api#schema)
</links>
