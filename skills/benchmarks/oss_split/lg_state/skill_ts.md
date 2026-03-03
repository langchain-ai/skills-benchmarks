---
name: langgraph-state-js
description: "[LangGraph] Managing state in LangGraph: schemas, reducers, channels, and message passing for coordinating agent execution"
---

<overview>
State is the central data structure in LangGraph that persists throughout graph execution. Proper state management is crucial for building reliable agents.

**Key Concepts:**
- **StateSchema**: Defines the structure and types of your state
- **Reducers**: Control how state updates are applied (ReducedValue)
- **Channels**: Low-level state management primitives
- **Message Passing**: How nodes communicate via state updates
</overview>

<decision-table>

| Need | Solution | Use Case |
|------|----------|----------|
| Overwrite value | Plain Zod schema | Simple fields like strings |
| Append to list | `ReducedValue` with concat | Logs, accumulating data |
| Custom logic | Custom reducer function | Complex merging, validation |
| Messages | `MessagesValue` | Chat applications |

</decision-table>

<ex-basic-state-management>
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
</ex-basic-state-management>

<ex-messages-with-reducer>
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
</ex-messages-with-reducer>

<ex-custom-reducer-with-reducedvalue>
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
</ex-custom-reducer-with-reducedvalue>

<ex-list-accumulation-with-reducedvalue>
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
</ex-list-accumulation-with-reducedvalue>

<ex-using-channels-api>
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
</ex-using-channels-api>

<ex-partial-state-updates>
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
</ex-partial-state-updates>

<boundaries>
**What You CAN Configure:**
- Define custom state schemas with Zod
- Add reducers via ReducedValue
- Create custom reducer functions
- Use built-in channels
- Use MessagesValue for chat
- Partial state updates
- Nested state structures

**What You CANNOT Configure:**
- Change state schema after compilation
- Access state outside node functions
- Modify state directly (must return updates)
- Share state between separate graphs
</boundaries>

<fix-forgot-reducer-for-arrays>
```typescript
// WRONG: Array will be overwritten
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
</fix-forgot-reducer-for-arrays>

<fix-state-updates-must-return-partial>
```typescript
// WRONG: Returning entire state object
const myNode = async (state: typeof State.State) => {
  state.field = "updated";
  return state;  // Don't do this!
};

// CORRECT: Return partial updates
const myNode = async (state: typeof State.State) => {
  return { field: "updated" };
};
```
</fix-state-updates-must-return-partial>

<fix-default-values>
```typescript
// RISKY: No default handling
const State = new StateSchema({
  count: z.number(),  // What if undefined?
});

const increment = async (state: typeof State.State) => {
  return { count: state.count + 1 };  // May error if count undefined
};

// BETTER: Use defaults in schema
const State = new StateSchema({
  count: z.number().default(0),
});
```
</fix-default-values>

<fix-always-await-nodes>
```typescript
// WRONG: Forgetting await
const result = graph.invoke({ input: "test" });
console.log(result.output);  // undefined (Promise!)

// CORRECT
const result = await graph.invoke({ input: "test" });
console.log(result.output);  // Works!
```
</fix-always-await-nodes>

<documentation-links>
- [StateSchema Guide](https://docs.langchain.com/oss/javascript/langgraph/graph-api#schema)
- [Channels API](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#channels-api)
- [ReducedValue](https://docs.langchain.com/oss/javascript/releases/changelog#standard-json-schema-support)
</documentation-links>
