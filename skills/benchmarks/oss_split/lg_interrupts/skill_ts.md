---
name: LangGraph Interrupts (TypeScript)
description: "[LangGraph] Human-in-the-loop with dynamic interrupts and breakpoints: pausing execution for human review and resuming with Command"
---

<overview>
Interrupts enable human-in-the-loop patterns by pausing graph execution for external input. LangGraph saves state and waits indefinitely until you resume execution.

**Key Types:**
- **Dynamic Interrupts**: `interrupt()` function called in nodes
- **Static Breakpoints**: `interruptBefore`/`interruptAfter` at compile time
</overview>

<decision-table>
| Type | When Set | Use Case |
|------|----------|----------|
| Dynamic (`interrupt()`) | Inside node code | Conditional pausing based on logic |
| Static (`interruptBefore`) | At compile time | Debug/test before specific nodes |
| Static (`interruptAfter`) | At compile time | Review output after specific nodes |
</decision-table>

<ex-dynamic-interrupt>
```typescript
import { interrupt, Command } from "@langchain/langgraph";
import { MemorySaver } from "@langchain/langgraph";

const reviewNode = async (state) => {
  // Conditionally pause for review
  if (state.needsReview) {
    // Pause and surface data to user
    const userResponse = interrupt({
      action: "review",
      data: state.draft,
      question: "Approve this draft?",
    });

    // userResponse comes from Command({ resume: ... })
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
  .compile({ checkpointer });  // Required!

// Initial invocation - will pause
const config = { configurable: { thread_id: "1" } };
const result = await graph.invoke(
  { needsReview: true, draft: "content" },
  config
);

// Check for interrupt
if ("__interrupt__" in result) {
  console.log(result.__interrupt__);  // See interrupt payload
}

// Resume with user decision
const finalResult = await graph.invoke(
  new Command({ resume: "approve" }),  // User's response
  config
);
```
</ex-dynamic-interrupt>

<ex-static-breakpoints>
```typescript
const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addNode("step3", step3)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", "step3")
  .addEdge("step3", END)
  .compile({
    checkpointer,
    interruptBefore: ["step2"],  // Pause before step2
    interruptAfter: ["step3"],   // Pause after step3
  });

const config = { configurable: { thread_id: "1" } };

// Run until first breakpoint
await graph.invoke({ data: "test" }, config);

// Resume (pauses at next breakpoint)
await graph.invoke(null, config);  // null = resume

// Resume again
await graph.invoke(null, config);
```
</ex-static-breakpoints>

<ex-tool-review-pattern>
```typescript
import { interrupt, Command } from "@langchain/langgraph";

const toolExecutor = async (state) => {
  const toolCalls = state.messages.at(-1)?.tool_calls || [];
  const results = [];

  for (const toolCall of toolCalls) {
    // Pause for each tool call
    const userDecision = interrupt({
      tool: toolCall.name,
      args: toolCall.args,
      question: "Execute this tool?",
    });

    let result;
    if (userDecision.type === "approve") {
      // Execute tool
      result = await executeTool(toolCall);
    } else if (userDecision.type === "edit") {
      // Use edited args
      result = await executeTool(userDecision.args);
    } else {  // reject
      result = "Tool execution rejected";
    }

    // Store result
    results.push(new ToolMessage({
      content: result,
      tool_call_id: toolCall.id,
    }));
  }

  return { messages: results };
};

// Usage
const result = await graph.invoke({ messages: [...] }, config);

// Review and approve
await graph.invoke(new Command({ resume: { type: "approve" } }), config);

// Or edit args
await graph.invoke(
  new Command({ resume: { type: "edit", args: { query: "modified" } } }),
  config
);

// Or reject
await graph.invoke(new Command({ resume: { type: "reject" } }), config);
```
</ex-tool-review-pattern>

<ex-editing-state-during-interrupt>
```typescript
const config = { configurable: { thread_id: "1" } };

// Run until interrupt
await graph.invoke({ data: "test" }, config);

// Modify state before resuming
await graph.updateState(config, { data: "manually edited" });

// Resume with edited state
await graph.invoke(null, config);
```
</ex-editing-state-during-interrupt>

<ex-stream-with-interrupts>
```typescript
const config = {
  configurable: { thread_id: "1" },
  streamMode: ["updates", "messages"] as const,
};

for await (const [mode, chunk] of await graph.stream({ query: "test" }, config)) {
  if (mode === "updates") {
    if ("__interrupt__" in chunk) {
      // Handle interrupt
      const interruptInfo = chunk.__interrupt__[0].value;
      const userInput = await getUserInput(interruptInfo);

      // Resume
      await graph.invoke(new Command({ resume: userInput }), config);
      break;
    }
  }
}
```
</ex-stream-with-interrupts>

<boundaries>
**What You CAN Configure:**
- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command({ resume: ... })`
- Edit state during interrupts
- Stream while handling interrupts
- Conditional interrupt logic

**What You CANNOT Configure:**
- Interrupt without checkpointer
- Modify interrupt mechanism
- Resume without thread_id
</boundaries>

<fix-checkpointer-required>
```typescript
// WRONG: No checkpointer
const graph = builder.compile();  // No persistence!
await graph.invoke(...);  // Interrupt won't work

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
</fix-checkpointer-required>

<fix-thread-id-required>
```typescript
// WRONG: No thread_id
await graph.invoke({ data: "test" });  // Can't resume!

// CORRECT
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```
</fix-thread-id-required>

<fix-resume-with-command-not-object>
```typescript
// WRONG: Passing regular object
await graph.invoke({ resumeData: "approve" }, config);  // Restarts!

// CORRECT: Use Command
import { Command } from "@langchain/langgraph";
await graph.invoke(new Command({ resume: "approve" }), config);
```
</fix-resume-with-command-not-object>

<fix-always-await>
```typescript
// WRONG
const result = graph.invoke({}, config);
console.log(result);  // Promise!

// CORRECT
const result = await graph.invoke({}, config);
console.log(result);
```
</fix-always-await>

<documentation-links>
- [Interrupts Guide](https://docs.langchain.com/oss/javascript/langgraph/interrupts)
- [Human-in-the-Loop](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [Command API](https://docs.langchain.com/oss/javascript/langgraph/graph-api#command)
</documentation-links>
