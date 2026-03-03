---
name: langgraph-fundamentals-js
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
| Need fine-grained control over agent orchestration | Quick prototyping -> LangChain agents |
| Building complex workflows with branching/loops | Simple stateless workflows -> LangChain direct |
| Require human-in-the-loop, persistence | Batteries-included features -> Deep Agents |

</when-to-use-langgraph>

---

## State Management

<state-update-strategies>

| Need | Solution | Example |
|------|----------|---------|
| Overwrite value | No reducer (default) | Simple fields like counters |
| Append to list | Reducer (operator.add / concat) | Message history, logs |
| Custom logic | Custom reducer function | Complex merging |

</state-update-strategies>

<ex-state-with-reducer>
Use StateSchema with ReducedValue for accumulating arrays.
```typescript
import { StateSchema, ReducedValue, MessagesValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  name: z.string(),  // Default: overwrites
  messages: MessagesValue,  // Built-in for messages
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
```
</ex-state-with-reducer>

<ex-messages-accumulating>
MessagesValue provides built-in accumulation for message arrays.
```typescript
import { StateSchema, MessagesValue, StateGraph, START, END } from "@langchain/langgraph";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

const State = new StateSchema({ messages: MessagesValue });

const addResponse = async (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  return { messages: [new AIMessage({ content: `Response to: ${lastMessage?.content}` })] };
};

// After invoke: messages list has BOTH original + response
```
</ex-messages-accumulating>

<fix-forgot-reducer-for-list>
Without ReducedValue, arrays are overwritten not appended.
```typescript
// WRONG: Array will be overwritten
const State = new StateSchema({
  items: z.array(z.string()),  // No reducer!
});
// Node 1: { items: ["A"] }, Node 2: { items: ["B"] }
// Final: { items: ["B"] }  // A is lost!

// CORRECT: Use ReducedValue
const State = new StateSchema({
  items: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
// Final: { items: ["A", "B"] }
```
</fix-forgot-reducer-for-list>

<fix-state-must-return-dict>
Return partial updates only, not the full state object.
```typescript
// WRONG: Returning entire state
const myNode = async (state: typeof State.State) => {
  state.field = "updated";
  return state;  // Don't do this!
};

// CORRECT: Return partial updates
const myNode = async (state: typeof State.State) => {
  return { field: "updated" };
};
```
</fix-state-must-return-dict>

---

## Building Graphs

<edge-type-selection>

| Need | Edge Type | When to Use |
|------|-----------|-------------|
| Always go to same node | `add_edge()` | Fixed, deterministic flow |
| Route based on state | `add_conditional_edges()` | Dynamic branching |
| Update state AND route | `Command` | Combine logic in single node |
| Fan-out to multiple nodes | `Send` | Parallel processing with dynamic inputs |

</edge-type-selection>

<ex-basic-graph>
Chain nodes with addEdge and compile before invoking.
```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  input: z.string(),
  output: z.string().default(""),
});

const processInput = async (state: typeof State.State) => {
  return { output: `Processed: ${state.input}` };
};

const finalize = async (state: typeof State.State) => {
  return { output: state.output.toUpperCase() };
};

const graph = new StateGraph(State)
  .addNode("process", processInput)
  .addNode("finalize", finalize)
  .addEdge(START, "process")
  .addEdge("process", "finalize")
  .addEdge("finalize", END)
  .compile();

const result = await graph.invoke({ input: "hello" });
console.log(result.output);  // "PROCESSED: HELLO"
```
</ex-basic-graph>

<ex-conditional-edges>
addConditionalEdges routes based on function return value.
```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  query: z.string(),
  route: z.string().default(""),
});

const classify = async (state: typeof State.State) => {
  if (state.query.toLowerCase().includes("weather")) {
    return { route: "weather" };
  }
  return { route: "general" };
};

const routeQuery = (state: typeof State.State) => state.route;

const graph = new StateGraph(State)
  .addNode("classify", classify)
  .addNode("weather", async () => ({ result: "Sunny, 72F" }))
  .addNode("general", async () => ({ result: "General response" }))
  .addEdge(START, "classify")
  .addConditionalEdges("classify", routeQuery, ["weather", "general"])
  .addEdge("weather", END)
  .addEdge("general", END)
  .compile();
```
</ex-conditional-edges>

<ex-command-state-and-routing>
Return Command with update and goto to combine state change with routing.
```typescript
import { StateGraph, StateSchema, START, END, Command } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number().default(0),
  result: z.string().default(""),
});

const nodeA = async (state: typeof State.State) => {
  const newCount = state.count + 1;
  if (newCount > 5) {
    return new Command({ update: { count: newCount }, goto: "node_c" });
  }
  return new Command({ update: { count: newCount }, goto: "node_b" });
};

const graph = new StateGraph(State)
  .addNode("node_a", nodeA)
  .addNode("node_b", async () => ({ result: "B" }))
  .addNode("node_c", async () => ({ result: "C" }))
  .addEdge(START, "node_a")
  .addEdge("node_b", END)
  .addEdge("node_c", END)
  .compile();
```
</ex-command-state-and-routing>

<ex-map-reduce-with-send>
Map items to Send objects for parallel execution.
```typescript
import { StateGraph, StateSchema, START, END, Send, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  items: z.array(z.string()),
  results: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (current, update) => current.concat(update)
  }),
});

const fanOut = (state: typeof State.State) =>
  state.items.map((item) => new Send("worker", { item }));

const worker = async (state: { item: string }) =>
  ({ results: [`Processed: ${state.item}`] });

const graph = new StateGraph(State)
  .addNode("worker", worker)
  .addConditionalEdges(START, fanOut, ["worker"])
  .addEdge("worker", END)
  .compile();
// invoke({ items: ["a", "b", "c"] }) -> results: ["Processed: a", "Processed: b", "Processed: c"]
```
</ex-map-reduce-with-send>

<ex-graph-with-loop>
Return END from conditional function to terminate loop.
```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  count: z.number().default(0),
  maxIterations: z.number(),
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };
};

const shouldContinue = (state: typeof State.State) => {
  if (state.count >= state.maxIterations) return END;
  return "increment";
};

const graph = new StateGraph(State)
  .addNode("increment", increment)
  .addEdge(START, "increment")
  .addConditionalEdges("increment", shouldContinue)
  .compile();

const result = await graph.invoke({ count: 0, maxIterations: 5 });
console.log(result.count);  // 5
```
</ex-graph-with-loop>

<fix-compile-before-execution>
Builder is not executable - compile first.
```typescript
// WRONG: Builder is not executable
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke({ input: "test" });  // Error!

// CORRECT: Must compile first
const graph = builder.compile();
await graph.invoke({ input: "test" });
```
</fix-compile-before-execution>

<fix-infinite-loop-needs-exit>
Use conditional edges with END return to break loops.
```typescript
// WRONG: Infinite loop
builder.addEdge("node_a", "node_b");
builder.addEdge("node_b", "node_a");  // Loops forever!

// CORRECT: Conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) return END;
  return "node_b";
};

builder.addConditionalEdges("node_a", shouldContinue);
```
</fix-infinite-loop-needs-exit>

<fix-always-await-nodes>
Always await graph.invoke() - it returns a Promise.
```typescript
// WRONG: Forgetting await
const result = graph.invoke({ input: "test" });
console.log(result.output);  // undefined (Promise!)

// CORRECT
const result = await graph.invoke({ input: "test" });
console.log(result.output);  // Works!
```
</fix-always-await-nodes>

<boundaries>
### What You CAN Configure

- Define custom state schemas with TypedDict/StateSchema
- Add reducers to control how state updates are merged
- Create nodes (any function)
- Add static and conditional edges
- Use Command for combined state/routing
- Create loops with conditional termination

### What You CANNOT Configure

- Modify START/END behavior
- Change the Pregel execution model
- Access state outside node functions
- Modify state directly (must return updates)
</boundaries>
