---
name: LangGraph Execution Control (TypeScript)
description: "INVOKE THIS SKILL for LangGraph workflows, parallel execution, interrupts, or streaming. Covers Send API for fan-out, interrupt() for human-in-the-loop, Command for resuming, and stream modes (values/updates/messages). CRITICAL: Fixes for interrupt without checkpointer, missing reducers for Send, and stream mode tuple unpacking."
---

<overview>
LangGraph provides execution control patterns for complex agent orchestration:

1. **Workflows vs Agents**: Predetermined paths vs dynamic decision-making
2. **Send API**: Fan-out to parallel workers (map-reduce)
3. **Interrupts**: Pause for human input, resume with Command
4. **Streaming**: Real-time state, tokens, and custom data
</overview>

<workflow-vs-agent>

| Characteristic | Workflow | Agent |
|----------------|----------|-------|
| **Control Flow** | Fixed, predetermined | Dynamic, model-driven |
| **Predictability** | High | Low |
| **Use Case** | Sequential tasks | Open-ended problems |

</workflow-vs-agent>

---

## Workflows and Agents

<ex-dynamic-agent>
Build a ReAct agent that dynamically decides when to call tools based on model responses.
```typescript
import { tool } from "@langchain/core/tools";
import { ChatOpenAI } from "@langchain/openai";
import { ToolMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const searchTool = tool(
  async ({ query }) => `Results for: ${query}`,
  { name: "search", description: "Search for information", schema: z.object({ query: z.string() }) }
);

const State = new StateSchema({ messages: MessagesValue });

const model = new ChatOpenAI({ model: "gpt-4" });
const modelWithTools = model.bindTools([searchTool]);

const agentNode = async (state: typeof State.State) => {
  const response = await modelWithTools.invoke(state.messages);
  return { messages: [response] };
};

const toolNode = async (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  const results = [];
  for (const toolCall of lastMessage.tool_calls ?? []) {
    const observation = await searchTool.invoke(toolCall.args);
    results.push(new ToolMessage({ content: observation, tool_call_id: toolCall.id }));
  }
  return { messages: results };
};

const shouldContinue = (state: typeof State.State) => {
  const lastMessage = state.messages.at(-1);
  return lastMessage?.tool_calls?.length ? "tools" : END;
};

const agent = new StateGraph(State)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile();
```
</ex-dynamic-agent>

<ex-orchestrator-worker>
Fan out tasks to parallel workers using the Send API and aggregate results.
```typescript
import { Send, StateGraph, StateSchema, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  tasks: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (curr, upd) => curr.concat(upd) }
  ),
});

const orchestrator = (state: typeof State.State) => {
  return state.tasks.map((task) => new Send("worker", { task }));
};

const worker = async (state: { task: string }) => {
  return { results: [`Completed: ${state.task}`] };
};

const synthesize = async (state: typeof State.State) => {
  return { summary: `Processed ${state.results.length} tasks` };
};

const graph = new StateGraph(State)
  .addNode("worker", worker)
  .addNode("synthesize", synthesize)
  .addConditionalEdges(START, orchestrator, ["worker"])
  .addEdge("worker", "synthesize")
  .addEdge("synthesize", END)
  .compile();
```
</ex-orchestrator-worker>

---

## Interrupts (Human-in-the-Loop)

<interrupt-type-selection>

| Type | When Set | Use Case |
|------|----------|----------|
| Dynamic (`interrupt()`) | Inside node code | Conditional pausing |
| Static (`interrupt_before`) | At compile time | Debug before nodes |
| Static (`interrupt_after`) | At compile time | Review after nodes |

</interrupt-type-selection>

<ex-dynamic-interrupt>
Pause execution for human review using dynamic interrupt and resume with Command.
```typescript
import { interrupt, Command, MemorySaver, StateGraph, START, END } from "@langchain/langgraph";

const reviewNode = async (state: typeof State.State) => {
  if (state.needsReview) {
    const userResponse = interrupt({
      action: "review",
      data: state.draft,
      question: "Approve this draft?"
    });
    if (userResponse === "reject") {
      return { status: "rejected" };
    }
  }
  return { status: "approved" };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("review", reviewNode)
  .addEdge(START, "review")
  .addEdge("review", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "1" } };
let result = await graph.invoke({ needsReview: true, draft: "content" }, config);

// Check for interrupt
if (result.__interrupt__) {
  console.log(result.__interrupt__);
}

// Resume with user decision
result = await graph.invoke(new Command({ resume: "approve" }), config);
```
</ex-dynamic-interrupt>

<ex-static-breakpoints>
Set compile-time breakpoints to pause before specific nodes.
```typescript
const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", END)
  .compile({
    checkpointer,
    interruptBefore: ["step2"],  // Pause before step2
  });

const config = { configurable: { thread_id: "1" } };
await graph.invoke({ data: "test" }, config);  // Runs until step2
await graph.invoke(null, config);  // Resume
```
</ex-static-breakpoints>

---

## Streaming

<stream-mode-selection>

| Mode | What it Streams | Use Case |
|------|----------------|----------|
| `values` | Full state after each step | Monitor complete state |
| `updates` | State deltas | Track incremental updates |
| `messages` | LLM tokens + metadata | Chat UIs |
| `custom` | User-defined data | Progress indicators |

</stream-mode-selection>

<ex-stream-llm-tokens>
Stream LLM tokens in real-time for chat UI display.
```typescript
for await (const chunk of graph.stream(
  { messages: [new HumanMessage("Hello")] },
  { streamMode: "messages" }
)) {
  const [token, metadata] = chunk;
  if (token.content) {
    process.stdout.write(token.content);
  }
}
```
</ex-stream-llm-tokens>

<ex-stream-custom-data>
Emit custom progress updates from within nodes using the stream writer.
```typescript
import { getStreamWriter } from "@langchain/langgraph";

const myNode = async (state: typeof State.State) => {
  const writer = getStreamWriter();
  writer("Processing step 1...");
  // Do work
  writer("Complete!");
  return { result: "done" };
};

for await (const chunk of graph.stream({ data: "test" }, { streamMode: "custom" })) {
  console.log(chunk);
}
```
</ex-stream-custom-data>

<boundaries>
### What You CAN Configure

- Choose workflow vs agent pattern
- Use Send API for parallel execution
- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)`
- Choose stream modes

### What You CANNOT Configure

- Interrupt without checkpointer
- Resume without thread_id
- Change Send API message-passing model
</boundaries>

<fix-send-accumulator>
Fix parallel worker results being overwritten by using a reducer to accumulate values.
```typescript
// WRONG: Last worker overwrites all others
const State = new StateSchema({
  results: z.array(z.string()),  // No reducer!
});

// CORRECT: Use ReducedValue
const State = new StateSchema({
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (curr, upd) => curr.concat(upd) }
  ),
});
```
</fix-send-accumulator>

<fix-checkpointer-required-for-interrupts>
Add a checkpointer to enable interrupt functionality (required for human-in-the-loop).
```typescript
// WRONG: No checkpointer - interrupt won't work
const graph = builder.compile();

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
</fix-checkpointer-required-for-interrupts>

<fix-resume-with-command>
Use Command to resume from an interrupt instead of passing a regular object.
```typescript
// WRONG: Passing regular object restarts graph
await graph.invoke({ resumeData: "approve" }, config);

// CORRECT: Use Command to resume
import { Command } from "@langchain/langgraph";
await graph.invoke(new Command({ resume: "approve" }), config);
```
</fix-resume-with-command>

<fix-agent-guardrails>
Add max iterations check to prevent infinite agent loops.
```typescript
// RISKY: Pure agent might loop forever
const shouldContinue = (state) => {
  if (state.messages.at(-1)?.tool_calls?.length) return "tools";
  return END;
};

// BETTER: Add max iterations check
const shouldContinue = (state) => {
  if (state.iterations > 10) return END;
  if (state.messages.at(-1)?.tool_calls?.length) return "tools";
  return END;
};
```
</fix-agent-guardrails>
