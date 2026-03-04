---
name: langgraph-graph-api
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

<decision-table>

| Need | Edge Type | When to Use |
|------|-----------|-------------|
| Always go to same node | `add_edge()` / `addEdge()` | Fixed, deterministic flow |
| Route based on state | `add_conditional_edges()` / `addConditionalEdges()` | Dynamic branching logic |
| Fan-out to multiple nodes | `Send` API | Map-reduce, parallel execution |
| Update state AND route | `Command` | Combine logic in single node |

</decision-table>

<key-concepts>
**1. Graph Execution Model**

LangGraph uses a **message-passing** model inspired by Google's Pregel:
- Execution proceeds in **super-steps** (discrete iterations)
- Nodes in parallel are part of the same super-step
- Sequential nodes belong to separate super-steps
- Graph ends when all nodes are inactive and no messages in transit

**2. Nodes**

**Nodes** are functions that:
- Receive the current state as input
- Perform computation or side effects
- Return state updates (partial or full)

<python>
Simple node returning state update:

```python
def my_node(state: State) -> dict:
    """Nodes are just functions!"""
    return {"key": "updated_value"}
```
</python>

<typescript>
Async node returning state update:

```typescript
const myNode = async (state: State): Promise<Partial<State>> => {
  // Nodes are just async functions!
  return { key: "updated_value" };
};
```
</typescript>

**3. Edges**

| Edge Type | Description | Python Example | TypeScript Example |
|-----------|-------------|----------------|-------------------|
| **Static** | Always routes to same node | `add_edge("A", "B")` | `addEdge("A", "B")` |
| **Conditional** | Routes based on state/logic | `add_conditional_edges("A", router)` | `addConditionalEdges("A", router)` |
| **Dynamic (Send)** | Fan-out to multiple nodes | `Send("worker", {...})` | `new Send("worker", {...})` |
| **Command** | State update + routing | `return Command(goto="B")` | `new Command({ goto: "B" })` |

**4. Special Nodes**

- **START**: Entry point of the graph (virtual node)
- **END**: Terminal node (graph halts)
</key-concepts>

<ex-basic>
<python>
Basic graph with static edges:

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
</python>

<typescript>
Basic graph with static edges:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

// 1. Define state
const State = new StateSchema({
  input: z.string(),
  output: z.string(),
});

// 2. Define nodes
const processInput = async (state: typeof State.State) => {
  return { output: `Processed: ${state.input}` };
};

const finalize = async (state: typeof State.State) => {
  return { output: state.output.toUpperCase() };
};

// 3. Build graph
const graph = new StateGraph(State)
  .addNode("process", processInput)
  .addNode("finalize", finalize)
  .addEdge(START, "process")       // Entry point
  .addEdge("process", "finalize")  // Static edge
  .addEdge("finalize", END)        // Exit point
  .compile();

// 4. Execute
const result = await graph.invoke({ input: "hello" });
console.log(result.output);  // "PROCESSED: HELLO"
```
</typescript>
</ex-basic>

<ex-conditional>
<python>
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
</python>

<typescript>
Router with conditional branching:

```typescript
import { StateGraph, StateSchema, ConditionalEdgeRouter, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  query: z.string(),
  route: z.string(),
  result: z.string().optional(),
});

const classify = async (state: typeof State.State) => {
  if (state.query.toLowerCase().includes("weather")) {
    return { route: "weather" };
  }
  return { route: "general" };
};

const weatherNode = async (state: typeof State.State) => {
  return { result: "Sunny, 72°F" };
};

const generalNode = async (state: typeof State.State) => {
  return { result: "General response" };
};

// Router function
const routeQuery: ConditionalEdgeRouter<typeof State, "weather" | "general"> = (state) => {
  return state.route as "weather" | "general";
};

const graph = new StateGraph(State)
  .addNode("classify", classify)
  .addNode("weather", weatherNode)
  .addNode("general", generalNode)
  .addEdge(START, "classify")
  // Conditional edge based on state
  .addConditionalEdges(
    "classify",
    routeQuery,
    ["weather", "general"]  // Possible destinations
  )
  .addEdge("weather", END)
  .addEdge("general", END)
  .compile();

const result = await graph.invoke({ query: "What's the weather?" });
```
</typescript>
</ex-conditional>

<ex-command>
<python>
Command combining state and routing:

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
</python>

<typescript>
Command combining state and routing:

```typescript
import { StateGraph, StateSchema, Command, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number(),
  result: z.string(),
});

const nodeA = async (state: typeof State.State) => {
  const newCount = state.count + 1;

  if (newCount > 5) {
    // Go to nodeC
    return new Command({
      update: { count: newCount, result: "Going to C" },
      goto: "nodeC"
    });
  } else {
    // Go to nodeB
    return new Command({
      update: { count: newCount, result: "Going to B" },
      goto: "nodeB"
    });
  }
};

const nodeB = async (state: typeof State.State) => {
  return { result: `B executed, count=${state.count}` };
};

const nodeC = async (state: typeof State.State) => {
  return { result: `C executed, count=${state.count}` };
};

const graph = new StateGraph(State)
  .addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] })  // Specify possible routes
  .addNode("nodeB", nodeB)
  .addNode("nodeC", nodeC)
  .addEdge(START, "nodeA")
  .addEdge("nodeB", END)
  .addEdge("nodeC", END)
  .compile();

const result1 = await graph.invoke({ count: 0 });
console.log(result1.result);  // "B executed, count=1"

const result2 = await graph.invoke({ count: 5 });
console.log(result2.result);  // "C executed, count=6"
```
</typescript>
</ex-command>

<ex-map-reduce>
<python>
Fan-out with Send API:

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
</python>

<typescript>
Fan-out with Send API:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  final: z.string().optional(),
});

const fanOut = (state: typeof State.State) => {
  // Send each item to a worker node
  return state.items.map(item =>
    new Send("worker", { item })
  );
};

const worker = async (state: { item: string }) => {
  // Process a single item
  return { results: [`Processed: ${state.item}`] };
};

const aggregate = async (state: typeof State.State) => {
  // Combine results
  return { final: state.results.join(", ") };
};

const graph = new StateGraph(State)
  .addNode("worker", worker)
  .addNode("aggregate", aggregate)
  .addConditionalEdges(START, fanOut, ["worker"])
  .addEdge("worker", "aggregate")
  .addEdge("aggregate", END)
  .compile();

const result = await graph.invoke({ items: ["A", "B", "C"] });
console.log(result.final);  // "Processed: A, Processed: B, Processed: C"
```
</typescript>
</ex-map-reduce>

<ex-loops>
<python>
Loop with conditional exit:

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
</python>

<typescript>
Loop with conditional exit:

```typescript
import { StateGraph, StateSchema, ConditionalEdgeRouter, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number(),
  maxIterations: z.number(),
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };
};

const shouldContinue: ConditionalEdgeRouter<typeof State, "increment"> = (state) => {
  if (state.count >= state.maxIterations) {
    return END;
  }
  return "increment";
};

const graph = new StateGraph(State)
  .addNode("increment", increment)
  .addEdge(START, "increment")
  .addConditionalEdges("increment", shouldContinue, ["increment", END])
  .compile();

const result = await graph.invoke({ count: 0, maxIterations: 5 });
console.log(result.count);  // 5
```
</typescript>
</ex-loops>

<ex-compile>
<python>
Compile with checkpointer and breakpoints:

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
</python>

<typescript>
Compile with checkpointer and breakpoints:

```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("nodeA", nodeA)
  .addEdge(START, "nodeA")
  .addEdge("nodeA", END)
  .compile({
    checkpointer,                    // Enable persistence
    interruptBefore: ["nodeA"],      // Breakpoint before node
    interruptAfter: ["nodeA"],       // Breakpoint after node
  });
```
</typescript>
</ex-compile>

<boundaries>
**What Agents CAN Configure**

- Define custom nodes (any function)
- Add static edges between nodes
- Add conditional edges with custom logic
- Use Command for combined state/routing
- Create loops with conditional termination
- Fan-out with Send API (map-reduce)
- Set breakpoints (interrupt_before/after or interruptBefore/After)
- Customize state schema
- Specify checkpointer for persistence

**What Agents CANNOT Configure**

- Modify START/END node behavior
- Change super-step execution model
- Alter message-passing protocol
- Override graph compilation logic
- Bypass state update mechanism
</boundaries>

<fix-compile-before-invoke>
<python>
Compile before invoking graph:

```python
# WRONG
builder = StateGraph(State).add_node("node", func)
builder.invoke({"input": "test"})  # AttributeError!

# CORRECT
graph = builder.compile()
graph.invoke({"input": "test"})
```
</python>
<typescript>
Compile before invoking graph:

```typescript
// WRONG
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke({ input: "test" });  // Error!

// CORRECT
const graph = builder.compile();
await graph.invoke({ input: "test" });
```
</typescript>
</fix-compile-before-invoke>

<fix-conditional-edge-destinations>
<python>
Add nodes before routing to them:

```python
# WRONG - "missing_node" not added to graph
def router(state):
    return "missing_node"

builder.add_conditional_edges("node_a", router, ["missing_node"])

# CORRECT - Add all possible destinations
builder.add_node("missing_node", func)
builder.add_conditional_edges("node_a", router, ["missing_node"])
```
</python>
<typescript>
Add nodes before routing to them:

```typescript
// WRONG - "missingNode" not added to graph
const router = (state) => "missingNode";

builder.addConditionalEdges("nodeA", router, ["missingNode"]);

// CORRECT - Add all possible destinations
builder.addNode("missingNode", func);
builder.addConditionalEdges("nodeA", router, ["missingNode"]);
```
</typescript>
</fix-conditional-edge-destinations>

<fix-command-type-annotation>
<python>
Specify destinations in type hint:

```python
# WRONG - No type hint for routing
def node_a(state) -> Command:
    return Command(goto="node_b")

# CORRECT - Specify possible destinations
from typing import Literal

def node_a(state) -> Command[Literal["node_b", "node_c"]]:
    return Command(goto="node_b")
```
</python>
<typescript>
Specify destinations with ends option:

```typescript
// WRONG - No ends specified
const nodeA = async (state) => {
  return new Command({ goto: "nodeB" });
};

builder.addNode("nodeA", nodeA);  // Error when using Command!

// CORRECT - Specify possible destinations
builder.addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] });
```
</typescript>
</fix-command-type-annotation>

<fix-loop-exit-condition>
<python>
Add exit condition to loops:

```python
# WRONG - Infinite loop
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # No way out!

# CORRECT - Conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
</python>
<typescript>
Add exit condition to loops:

```typescript
// WRONG - Infinite loop
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // No way out!

// CORRECT - Conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) return END;
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue, ["nodeB", END]);
```
</typescript>
</fix-loop-exit-condition>

<fix-send-api-reducer>
<python>
Use reducer for parallel results:

```python
# WRONG - Results will be overwritten
class State(TypedDict):
    results: list  # No reducer!

# CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates results
```
</python>
<typescript>
Use ReducedValue for parallel results:

```typescript
// WRONG - Results will be overwritten
const State = new StateSchema({
  results: z.array(z.string()),  // No reducer!
});

// CORRECT - Use ReducedValue
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
```
</typescript>
</fix-send-api-reducer>

<fix-start-not-destination>
<python>
Use named entry node instead:

```python
# WRONG - Cannot route back to START
builder.add_edge("node_a", START)  # Error!

# CORRECT - Use named entry node instead
builder.add_node("entry", entry_func)
builder.add_edge(START, "entry")
builder.add_edge("node_a", "entry")  # OK
```
</python>
<typescript>
Use named entry node instead:

```typescript
// WRONG - Cannot route back to START
builder.addEdge("nodeA", START);  // Error!

// CORRECT - Use named entry node instead
builder.addNode("entry", entryFunc);
builder.addEdge(START, "entry");
builder.addEdge("nodeA", "entry");  // OK
```
</typescript>
</fix-start-not-destination>

<fix-await-invoke>
<typescript>
Await async graph invocations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ input: "test" });
console.log(result.output);  // undefined (Promise!)

// CORRECT
const result = await graph.invoke({ input: "test" });
console.log(result.output);  // Works!
```
</typescript>
</fix-await-invoke>

<links>
**Python**
- [Graph API Reference (Python)](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Using the Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [Command Documentation](https://docs.langchain.com/oss/python/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)
- [Send API Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Conditional Branching](https://docs.langchain.com/oss/python/langgraph/use-graph-api#conditional-branching)

**TypeScript**
- [Graph API Reference (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/graph-api)
- [Using the Graph API](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api)
- [Command Documentation](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)
- [Send API Guide](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Conditional Branching](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#create-and-control-loops)
</links>
