---
name: LangGraph Interrupts
description: "[LangGraph] Human-in-the-loop with dynamic interrupts and breakpoints: pausing execution for human review and resuming with Command"
---


## Overview

Interrupts enable human-in-the-loop patterns by pausing graph execution for external input. LangGraph saves state and waits indefinitely until you resume execution.

**Key Types:**
- **Dynamic Interrupts**: `interrupt()` function called in nodes
- **Static Breakpoints**: `interrupt_before`/`interrupt_after` (Python) or `interruptBefore`/`interruptAfter` (TypeScript) at compile time

## Decision Table: Interrupt Types

| Type | When Set | Use Case |
|------|----------|----------|
| Dynamic (`interrupt()`) | Inside node code | Conditional pausing based on logic |
| Static (`interrupt_before` / `interruptBefore`) | At compile time | Debug/test before specific nodes |
| Static (`interrupt_after` / `interruptAfter`) | At compile time | Review output after specific nodes |

## Code Examples

### Dynamic Interrupt

#### Python
```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

def review_node(state):
    # Conditionally pause for review
    if state["needs_review"]:
        # Pause and surface data to user
        user_response = interrupt({
            "action": "review",
            "data": state["draft"],
            "question": "Approve this draft?"
        })

        # user_response comes from Command(resume=...)
        if user_response == "reject":
            return {"status": "rejected"}

    return {"status": "approved"}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("review", review_node)
    .add_edge(START, "review")
    .add_edge("review", END)
    .compile(checkpointer=checkpointer)  # Required!
)

# Initial invocation - will pause
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"needs_review": True, "draft": "content"}, config)

# Check for interrupt
if "__interrupt__" in result:
    print(result["__interrupt__"])  # See interrupt payload

# Resume with user decision
from langgraph.types import Command
result = graph.invoke(
    Command(resume="approve"),  # User's response
    config
)
```

#### TypeScript
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

### Static Breakpoints

#### Python
```python
checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_node("step3", step3)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", "step3")
    .add_edge("step3", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"],  # Pause before step2
        interrupt_after=["step3"]    # Pause after step3
    )
)

config = {"configurable": {"thread_id": "1"}}

# Run until first breakpoint
graph.invoke({"data": "test"}, config)

# Resume (pauses at next breakpoint)
graph.invoke(None, config)  # None = resume

# Resume again
graph.invoke(None, config)
```

#### TypeScript
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

### Tool Review Pattern

#### Python
```python
from langgraph.types import interrupt, Command

def tool_executor(state):
    tool_calls = state["messages"][-1].tool_calls

    for tool_call in tool_calls:
        # Pause for each tool call
        user_decision = interrupt({
            "tool": tool_call["name"],
            "args": tool_call["args"],
            "question": "Execute this tool?"
        })

        if user_decision["type"] == "approve":
            # Execute tool
            result = execute_tool(tool_call)
        elif user_decision["type"] == "edit":
            # Use edited args
            result = execute_tool(user_decision["args"])
        else:  # reject
            result = "Tool execution rejected"

        # Store result
        results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    return {"messages": results}

# Usage
result = graph.invoke({"messages": [...]}, config)

# Review and approve
graph.invoke(Command(resume={"type": "approve"}), config)

# Or edit args
graph.invoke(
    Command(resume={"type": "edit", "args": {"query": "modified"}}),
    config
)

# Or reject
graph.invoke(Command(resume={"type": "reject"}), config)
```

#### TypeScript
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

### Editing State During Interrupt

#### Python
```python
config = {"configurable": {"thread_id": "1"}}

# Run until interrupt
graph.invoke({"data": "test"}, config)

# Modify state before resuming
graph.update_state(config, {"data": "manually edited"})

# Resume with edited state
graph.invoke(None, config)
```

#### TypeScript
```typescript
const config = { configurable: { thread_id: "1" } };

// Run until interrupt
await graph.invoke({ data: "test" }, config);

// Modify state before resuming
await graph.updateState(config, { data: "manually edited" });

// Resume with edited state
await graph.invoke(null, config);
```

### Stream with Interrupts

#### Python
```python
async for mode, chunk in graph.astream(
    {"query": "test"},
    stream_mode=["updates", "messages"],
    config={"configurable": {"thread_id": "1"}}
):
    if mode == "updates":
        if "__interrupt__" in chunk:
            # Handle interrupt
            interrupt_info = chunk["__interrupt__"][0].value
            user_input = get_user_input(interrupt_info)

            # Resume
            initial_input = Command(resume=user_input)
            break
```

#### TypeScript
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

## Boundaries

### What You CAN Configure

- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)` or `new Command({ resume: ... })`
- Edit state during interrupts
- Stream while handling interrupts
- Conditional interrupt logic

### What You CANNOT Configure

- Interrupt without checkpointer
- Modify interrupt mechanism
- Resume without thread_id

## Gotchas

### 1. Checkpointer Required

#### Python
```python
# WRONG - No checkpointer
graph = builder.compile()  # No persistence!
graph.invoke(...)  # Interrupt won't work

# CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

#### TypeScript
```typescript
// WRONG - No checkpointer
const graph = builder.compile();  // No persistence!
await graph.invoke(...);  // Interrupt won't work

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```

### 2. Thread ID Required

#### Python
```python
# WRONG - No thread_id
graph.invoke({"data": "test"})  # Can't resume!

# CORRECT
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```

#### TypeScript
```typescript
// WRONG - No thread_id
await graph.invoke({ data: "test" });  // Can't resume!

// CORRECT
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```

### 3. Resume with Command, Not Dict/Object

#### Python
```python
# WRONG - Passing regular dict
graph.invoke({"resume_data": "approve"}, config)  # Restarts!

# CORRECT - Use Command
from langgraph.types import Command
graph.invoke(Command(resume="approve"), config)
```

#### TypeScript
```typescript
// WRONG - Passing regular object
await graph.invoke({ resumeData: "approve" }, config);  // Restarts!

// CORRECT - Use Command
import { Command } from "@langchain/langgraph";
await graph.invoke(new Command({ resume: "approve" }), config);
```

### 4. Static Breakpoints Not Recommended for HITL (Python)

```python
# ANTI-PATTERN - Static breakpoints for all users
compile(interrupt_before=["action"])  # Pauses for everyone!

# BETTER - Dynamic interrupts with logic
def node(state):
    if state["requires_approval"]:  # Conditional
        interrupt({"action": "approve?"})
```

### 5. Always Await (TypeScript)

```typescript
// WRONG
const result = graph.invoke({}, config);
console.log(result);  // Promise!

// CORRECT
const result = await graph.invoke({}, config);
console.log(result);
```

## Links

### Python
- [Interrupts Guide](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Command API](https://docs.langchain.com/oss/python/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)

### TypeScript
- [Interrupts Guide](https://docs.langchain.com/oss/javascript/langgraph/interrupts)
- [Human-in-the-Loop](https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop)
- [Command API](https://docs.langchain.com/oss/javascript/langgraph/graph-api#command)
