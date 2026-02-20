---
name: Deep Agents Orchestration (TypeScript)
description: "INVOKE THIS SKILL when using subagents, task planning, or human approval in Deep Agents. Covers SubAgentMiddleware, TodoList for planning, and HITL interrupts. CRITICAL: Fixes for custom subagents NOT inheriting skills (must specify explicitly), interrupt_on requiring checkpointer, and subagent statelessness."
---

<overview>
Deep Agents include three orchestration capabilities:

1. **SubAgentMiddleware**: Delegate work via `task` tool to specialized agents
2. **TodoListMiddleware**: Plan and track tasks via `write_todos` tool
3. **HumanInTheLoopMiddleware**: Require approval before sensitive operations

All three are automatically included in `createDeepAgent()`.
</overview>

---

## Subagents (Task Delegation)

<when-to-use-subagents>

| Use Subagents When | Use Main Agent When |
|-------------------|-------------------|
| Task needs specialized tools | General-purpose tools sufficient |
| Want to isolate complex work | Single-step operation |
| Need clean context for main agent | Context bloat acceptable |

</when-to-use-subagents>

<how-subagents-work>
Main agent has `task` tool -> creates fresh subagent -> subagent executes autonomously -> returns final report.

**Default subagent**: "general-purpose" - automatically available with same tools/config as main agent.
</how-subagents-work>

<ex-custom-subagents>
Create a custom "researcher" subagent with specialized tools for academic paper search.
```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchPapers = tool(
  async ({ query }) => `Found 10 papers about ${query}`,
  { name: "search_papers", description: "Search papers", schema: z.object({ query: z.string() }) }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "researcher",
      description: "Conduct web research and compile findings",
      systemPrompt: "Search thoroughly, return concise summary",
      tools: [searchPapers],
    }
  ]
});

// Main agent delegates: task(agent="researcher", instruction="Research AI trends")
```
</ex-custom-subagents>

<fix-subagents-are-stateless>
Demonstrate that subagents are stateless and require complete instructions in a single call.
```typescript
// WRONG: Subagents don't remember previous calls
await agent.invoke({ messages: [{ role: "user", content: "task research: Find data" }] });
await agent.invoke({ messages: [{ role: "user", content: "task research: What did you find?" }] });
// Second call starts fresh

// CORRECT: Provide complete instructions upfront
```
</fix-subagents-are-stateless>

---

## TodoList (Task Planning)

<when-to-use-todolist>

| Use TodoList When | Skip TodoList When |
|------------------|-------------------|
| Complex multi-step tasks | Simple single-action tasks |
| Long-running operations | Quick operations (< 3 steps) |

</when-to-use-todolist>

<todolist-tool>
```
write_todos(todos: list[dict]) -> None
```

Each todo item has:
- `content`: Description of the task
- `status`: One of `"pending"`, `"in_progress"`, `"completed"`
</todolist-tool>

<ex-todolist-usage>
Invoke an agent that automatically creates a todo list for a multi-step task.
```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent();  // TodoListMiddleware included

const result = await agent.invoke({
  messages: [{ role: "user", content: "Create a REST API: design models, implement CRUD, add auth, write tests" }]
}, { configurable: { thread_id: "session-1" } });
```
</ex-todolist-usage>

---

## Human-in-the-Loop (Approval Workflows)

<when-to-use-hitl>

| Use HITL When | Skip HITL When |
|--------------|---------------|
| High-stakes operations (DB writes, deployments) | Read-only operations |
| Compliance requires human oversight | Fully automated workflows |

</when-to-use-hitl>

<ex-hitl-setup>
Configure which tools require human approval before execution.
```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: {
    write_file: true,
    execute_sql: { allowedDecisions: ["approve", "reject"] },
    read_file: false,
  },
  checkpointer: new MemorySaver()  // REQUIRED
});
```
</ex-hitl-setup>

<ex-approval-workflow>
Complete workflow: trigger an interrupt, check state, approve action, and resume execution.
```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver, Command } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

// Step 1: Agent proposes write_file - execution pauses
let result = await agent.invoke({
  messages: [{ role: "user", content: "Write config to /prod.yaml" }]
}, config);

// Step 2: Check for interrupts
const state = await agent.getState(config);
if (state.next) {
  console.log("Pending action");
}

// Step 3: Approve
await agent.updateState(config, {
  messages: [new Command({ resume: { decisions: [{ type: "approve" }] } })]
});

// Step 4: Resume
result = await agent.invoke(null, config);
```
</ex-approval-workflow>

<ex-reject-with-feedback>
Reject a pending action with feedback, prompting the agent to try a different approach.
```typescript
await agent.updateState(config, {
  messages: [new Command({ resume: { decisions: [{ type: "reject", message: "Run tests first" }] } })]
});
const result = await agent.invoke(null, config);
```
</ex-reject-with-feedback>

<boundaries>
### What Agents CAN Configure

- Subagent names, tools, models, system prompts
- Which tools require approval
- Allowed decision types per tool
- TodoList content and structure

### What Agents CANNOT Configure

- Tool names (`task`, `write_todos`)
- HITL protocol (approve/edit/reject structure)
- Skip checkpointer requirement for interrupts
- Make subagents stateful (they're ephemeral)
</boundaries>

<fix-checkpointer-required>
Show that a checkpointer is required when using interruptOn for HITL workflows.
```typescript
// WRONG: Checkpointer required
const agent = await createDeepAgent({ interruptOn: { write_file: true } });

// CORRECT: Must provide checkpointer
const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
</fix-checkpointer-required>

<fix-thread-id-required-for-resumption>
Demonstrate that a consistent thread_id is required to resume interrupted workflows.
```typescript
// WRONG: Can't resume without thread_id
await agent.invoke({ messages: [...] });
await agent.updateState(...);  // Which thread?

// CORRECT: Use consistent thread_id
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [...] }, config);
await agent.updateState(config, ...);
await agent.invoke(null, config);  // Resume
```
</fix-thread-id-required-for-resumption>
