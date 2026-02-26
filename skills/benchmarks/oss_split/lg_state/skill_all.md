---
name: LangGraph State
description: "[LangGraph] Managing state in LangGraph: schemas, reducers, channels, and message passing for coordinating agent execution"
---

<overview>
State is the central data structure in LangGraph that persists throughout graph execution. Proper state management is crucial for building reliable agents.

**Key Concepts:**
- **State Schema**: Defines the structure and types of your state (TypedDict in Python, StateSchema with Zod in TypeScript)
- **Reducers**: Control how state updates are applied
- **Channels**: Low-level state management primitives
- **Message Passing**: How nodes communicate via state updates
</overview>

<decision-table>

| Need | Python Solution | TypeScript Solution | Use Case |
|------|-----------------|---------------------|----------|
| Overwrite value | No reducer (default) | Plain Zod schema | Simple fields like strings |
| Append to list | `operator.add` | `ReducedValue` with concat | Message history, logs |
| Custom logic | Custom reducer function | Custom reducer function | Complex merging, validation |
| Messages | `Annotated[list, add_messages]` | `MessagesValue` | Chat applications |

</decision-table>

<key-concepts>
**1. State Schema**

<python>
Define state with TypedDict:

```python
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str
    count: int
```
</python>

<typescript>
Define state with StateSchema and Zod:

```typescript
import { StateSchema } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  input: z.string(),
  output: z.string(),
  count: z.number(),
});
```
</typescript>

**2. Reducers**

Reducers determine how updates are merged with existing state.

<python>
State with reducers:

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
</python>

<typescript>
State with ReducedValue:

```typescript
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  // Default: overwrites
  name: z.string(),

  // Reducer: appends to array
  messages: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),

  // Reducer: sums numbers
  total: new ReducedValue(
    z.number().default(0),
    { reducer: (current, update) => current + update }
  ),
});
```
</typescript>

**3. Channels API**

For advanced state control:

| Channel Type | Behavior |
|-------------|----------|
| `LastValue` | Stores most recent value |
| `BinaryOperatorAggregate` | Combines with reducer |
| `Topic` | Collects all values |
| `EphemeralValue` | Resets between supersteps |

</key-concepts>

<ex-basic>
<python>
Simple state with partial updates:

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
</python>

<typescript>
Simple state with partial updates:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  input: z.string(),
  processed: z.string(),
  count: z.number(),
});

const process = async (state: typeof State.State) => {
  return {
    processed: state.input.toUpperCase(),
    count: state.count + 1,
  };
};

const graph = new StateGraph(State)
  .addNode("process", process)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile();

const result = await graph.invoke({ input: "hello", count: 0 });
console.log(result);  // { input: 'hello', processed: 'HELLO', count: 1 }
```
</typescript>
</ex-basic>

<ex-messages>
<python>
Accumulate messages with operator.add:

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
</python>

<typescript>
Accumulate messages with MessagesValue:

```typescript
import { StateSchema, MessagesValue, StateGraph, START, END } from "@langchain/langgraph";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

const MessagesState = new StateSchema({
  messages: MessagesValue,
});

const addResponse = async (state: typeof MessagesState.State) => {
  const lastMessage = state.messages.at(-1);
  const userMsg = lastMessage?.content || "";
  return {
    messages: [new AIMessage({ content: `Response to: ${userMsg}` })],
  };
};

const graph = new StateGraph(MessagesState)
  .addNode("respond", addResponse)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile();

const result = await graph.invoke({
  messages: [new HumanMessage({ content: "Hello!" })],
});
console.log(result.messages.length);  // 2 (original + response)
```
</typescript>
</ex-messages>

<ex-custom-reducer>
<python>
Custom function to merge dictionaries:

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
</python>

<typescript>
Custom reducer to merge objects:

```typescript
import { StateSchema, ReducedValue, START, END, StateGraph } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  metadata: new ReducedValue(
    z.record(z.string(), z.any()).default(() => ({})),
    {
      inputSchema: z.record(z.string(), z.any()),
      reducer: (current, update) => ({ ...current, ...update }),
    }
  ),
  data: z.string(),
});

const updateMetadata = async (state: typeof State.State) => {
  return { metadata: { timestamp: "2024-01-01" } };
};

const graph = new StateGraph(State)
  .addNode("update", updateMetadata)
  .addEdge(START, "update")
  .addEdge("update", END)
  .compile();

const result = await graph.invoke({
  metadata: { user: "alice" },
  data: "test",
});
// metadata is merged: { user: "alice", timestamp: "2024-01-01" }
```
</typescript>
</ex-custom-reducer>

<ex-list>
<python>
Append items with operator.add:

```python
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]

def add_items(state: State) -> dict:
    return {"items": ["new_item"]}

graph = (
    StateGraph(State)
    .add_node("add", add_items)
    .add_edge(START, "add")
    .add_edge("add", END)
    .compile()
)

result = graph.invoke({"items": ["old1", "old2"]})
print(result["items"])  # ['old1', 'old2', 'new_item']
```
</python>

<typescript>
Append items with concat reducer:

```typescript
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      inputSchema: z.array(z.string()),
      reducer: (current, update) => current.concat(update),
    }
  ),
});

const addItems = async (state: typeof State.State) => {
  return { items: ["new_item"] };
};

const graph = new StateGraph(State)
  .addNode("add", addItems)
  .addEdge(START, "add")
  .addEdge("add", END)
  .compile();

const result = await graph.invoke({ items: ["old1", "old2"] });
console.log(result.items);  // ['old1', 'old2', 'new_item']
```
</typescript>
</ex-list>

<ex-overwrite>
<python>
Bypass reducer with Overwrite:

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
</python>
</ex-overwrite>

<ex-channels>
<python>
Low-level channel configuration:

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
</python>

<typescript>
Low-level channel configuration:

```typescript
import { StateGraph, LastValue, BinaryOperatorAggregate } from "@langchain/langgraph";

interface State {
  counter: number;
  logs: string[];
}

const graph = new StateGraph<State>({
  channels: {
    counter: new BinaryOperatorAggregate<number>(
      (x, y) => x + y,
      () => 0
    ),
    logs: new BinaryOperatorAggregate<string[]>(
      (x, y) => x.concat(y),
      () => []
    ),
  },
});
```
</typescript>
</ex-channels>

<ex-partial>
<python>
Update only specific fields:

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
</python>

<typescript>
Update only specific fields:

```typescript
import { StateSchema, StateGraph, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  field1: z.string(),
  field2: z.string(),
  field3: z.string(),
});

const updateField1 = async (state: typeof State.State) => {
  // Only update field1, others unchanged
  return { field1: "updated" };
};

const updateField2 = async (state: typeof State.State) => {
  // Only update field2
  return { field2: "also updated" };
};

const graph = new StateGraph(State)
  .addNode("node1", updateField1)
  .addNode("node2", updateField2)
  .addEdge(START, "node1")
  .addEdge("node1", "node2")
  .addEdge("node2", END)
  .compile();

const result = await graph.invoke({
  field1: "original1",
  field2: "original2",
  field3: "original3",
});
// field1: "updated", field2: "also updated", field3: "original3"
```
</typescript>
</ex-partial>

<boundaries>
**What You CAN Configure**

- Define custom state schemas
- Add reducers to fields
- Create custom reducer functions
- Use built-in channels
- Bypass reducers with Overwrite (Python)
- Partial state updates
- Nested state structures
- Use MessagesValue for chat (TypeScript)

**What You CANNOT Configure**

- Change state after graph compilation
- Access state outside node functions
- Modify state directly (must return updates)
- Share state between separate graphs
</boundaries>

<fix-list-reducer>
<python>
Add reducer for list accumulation:

```python
# WRONG - List will be overwritten
class State(TypedDict):
    items: list  # No reducer!

# Node 1 returns: {"items": ["A"]}
# Node 2 returns: {"items": ["B"]}
# Final state: {"items": ["B"]}  # A is lost!

# CORRECT
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]
# Final state: {"items": ["A", "B"]}
```
</python>

<typescript>
Add ReducedValue for array accumulation:

```typescript
// WRONG - Array will be overwritten
const State = new StateSchema({
  items: z.array(z.string()),  // No reducer!
});

// Node 1 returns: { items: ["A"] }
// Node 2 returns: { items: ["B"] }
// Final state: { items: ["B"] }  // A is lost!

// CORRECT
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
// Final state: { items: ["A", "B"] }
```
</typescript>
</fix-list-reducer>

<fix-return-partial>
<python>
Return partial updates only:

```python
# WRONG - Returning entire state object
def my_node(state: State) -> State:
    state["field"] = "updated"
    return state  # Don't do this!

# CORRECT - Return dict with updates
def my_node(state: State) -> dict:
    return {"field": "updated"}
```
</python>

<typescript>
Return partial updates only:

```typescript
// WRONG - Returning entire state object
const myNode = async (state: typeof State.State) => {
  state.field = "updated";
  return state;  // Don't do this!
};

// CORRECT - Return partial updates
const myNode = async (state: typeof State.State) => {
  return { field: "updated" };
};
```
</typescript>
</fix-return-partial>

<fix-default-values>
<python>
Handle missing values safely:

```python
# RISKY - No default, may cause errors
class State(TypedDict):
    count: int  # What if not initialized?

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}  # KeyError!

# BETTER - Use .get() with default
def increment(state: State) -> dict:
    return {"count": state.get("count", 0) + 1}
```
</python>

<typescript>
Use defaults in schema:

```typescript
// RISKY - No default handling
const State = new StateSchema({
  count: z.number(),  // What if undefined?
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };  // May error if count undefined
};

// BETTER - Use defaults in schema
const State = new StateSchema({
  count: z.number().default(0),
});
```
</typescript>
</fix-default-values>

<fix-reducer-type-mismatch>
<python>
Return correct type for reducer:

```python
# WRONG - Reducer expects list, but receives string
class State(TypedDict):
    items: Annotated[list, operator.add]

def bad_update(state: State) -> dict:
    return {"items": "not a list"}  # Type error!

# CORRECT
def good_update(state: State) -> dict:
    return {"items": ["item"]}
```
</python>
</fix-reducer-type-mismatch>

<fix-await-nodes>
<typescript>
Await async invocations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ input: "test" });
console.log(result.output);  // undefined (Promise!)

// CORRECT
const result = await graph.invoke({ input: "test" });
console.log(result.output);  // Works!
```
</typescript>
</fix-await-nodes>

<links>
**Python**
- [State Management Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#process-state-updates-with-reducers)
- [Channels API](https://docs.langchain.com/oss/python/langgraph/use-graph-api#channels-api)
- [Schema Reference](https://docs.langchain.com/oss/python/langgraph/graph-api#schema)

**TypeScript**
- [StateSchema Guide](https://docs.langchain.com/oss/javascript/langgraph/graph-api#schema)
- [Channels API](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#channels-api)
- [ReducedValue](https://docs.langchain.com/oss/javascript/releases/changelog#standard-json-schema-support)
</links>
