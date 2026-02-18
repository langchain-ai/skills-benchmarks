---
name: LangGraph Graph API (TypeScript)
description: [LangGraph] Building graphs with StateGraph, nodes, edges, START/END nodes, and the Command API for combining control flow with state updates
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
| Always go to same node | `addEdge()` | Fixed, deterministic flow |
| Route based on state | `addConditionalEdges()` | Dynamic branching logic |
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

**Nodes** are async functions that:
- Receive the current state as input
- Perform computation or side effects
- Return state updates (partial or full)

```typescript
const myNode = async (state: State): Promise<Partial<State>> => {
  // Nodes are just async functions!
  return { key: "updated_value" };
};
```

**3. Edges**

| Edge Type | Description | Example |
|-----------|-------------|---------|
| **Static** | Always routes to same node | `addEdge("A", "B")` |
| **Conditional** | Routes based on state/logic | `addConditionalEdges("A", router)` |
| **Dynamic (Send)** | Fan-out to multiple nodes | `new Send("worker", {...})` |
| **Command** | State update + routing | `new Command({ goto: "B" })` |

**4. Special Nodes**

- **START**: Entry point of the graph (virtual node)
- **END**: Terminal node (graph halts)
</key-concepts>

<ex-basic-graph-with-static-edges>
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
</ex-basic-graph-with-static-edges>

<ex-conditional-edges-branching>
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
</ex-conditional-edges-branching>

<ex-using-command-for-state-routing>
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
</ex-using-command-for-state-routing>

<ex-map-reduce-with-send-api>
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
</ex-map-reduce-with-send-api>

<ex-graph-with-loops>
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
</ex-graph-with-loops>

<ex-compiling-with-options>
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
</ex-compiling-with-options>

<boundaries>
**What Agents CAN Configure:**
- Define custom nodes (any async function)
- Add static edges between nodes
- Add conditional edges with custom logic
- Use Command for combined state/routing
- Create loops with conditional termination
- Fan-out with Send API (map-reduce)
- Set breakpoints (interruptBefore/After)
- Customize state schema
- Specify checkpointer for persistence

**What Agents CANNOT Configure:**
- Modify START/END node behavior
- Change super-step execution model
- Alter message-passing protocol
- Override graph compilation logic
- Bypass state update mechanism
</boundaries>

<fix-must-compile-before-execution>
```typescript
// WRONG
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke({ input: "test" });  // Error!

// CORRECT
const graph = builder.compile();
await graph.invoke({ input: "test" });
```
</fix-must-compile-before-execution>

<fix-conditional-edge-destinations-must-exist>
```typescript
// WRONG: "missingNode" not added to graph
const router = (state) => "missingNode";

builder.addConditionalEdges("nodeA", router, ["missingNode"]);

// CORRECT: Add all possible destinations
builder.addNode("missingNode", func);
builder.addConditionalEdges("nodeA", router, ["missingNode"]);
```
</fix-conditional-edge-destinations-must-exist>

<fix-command-requires-ends-parameter>
```typescript
// WRONG: No ends specified
const nodeA = async (state) => {
  return new Command({ goto: "nodeB" });
};

builder.addNode("nodeA", nodeA);  // Error when using Command!

// CORRECT: Specify possible destinations
builder.addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] });
```
</fix-command-requires-ends-parameter>

<fix-loops-need-exit-condition>
```typescript
// WRONG: Infinite loop
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // No way out!

// CORRECT: Conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) return END;
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue, ["nodeB", END]);
```
</fix-loops-need-exit-condition>

<fix-send-api-requires-reducer>
```typescript
// WRONG: Results will be overwritten
const State = new StateSchema({
  results: z.array(z.string()),  // No reducer!
});

// CORRECT: Use ReducedValue
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
```
</fix-send-api-requires-reducer>

<fix-start-is-virtual-cannot-be-destination>
```typescript
// WRONG: Cannot route back to START
builder.addEdge("nodeA", START);  // Error!

// CORRECT: Use named entry node instead
builder.addNode("entry", entryFunc);
builder.addEdge(START, "entry");
builder.addEdge("nodeA", "entry");  // OK
```
</fix-start-is-virtual-cannot-be-destination>

<fix-always-use-await>
```typescript
// WRONG: Forgetting await
const result = graph.invoke({ input: "test" });
console.log(result.output);  // undefined (Promise!)

// CORRECT
const result = await graph.invoke({ input: "test" });
console.log(result.output);  // Works!
```
</fix-always-use-await>

<documentation-links>
- [Graph API Reference (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/graph-api)
- [Using the Graph API](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api)
- [Command Documentation](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)
- [Send API Guide](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Conditional Branching](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#create-and-control-loops)
</documentation-links>
