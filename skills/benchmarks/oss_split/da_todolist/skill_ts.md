---
name: Deep Agents Todo List (TypeScript)
description: "[Deep Agents] Using TodoListMiddleware for task planning and tracking progress with the write_todos tool in Deep Agents for complex multi-step workflows."
---

<overview>
TodoListMiddleware provides agents with task planning and progress tracking capabilities through the `write_todos` tool. It's automatically included in every deep agent and helps agents break down complex, multi-step tasks into manageable pieces.
</overview>

<when-to-use>
| Use TodoList When | Skip TodoList When |
|------------------|-------------------|
| Complex multi-step tasks requiring coordination | Simple, single-action tasks |
| Long-running operations where progress visibility matters | Quick operations (< 3 steps) |
| Tasks that may need plan adaptation | Fixed, predetermined workflows |
</when-to-use>

<ex-default-config>
```typescript
import { createDeepAgent } from "deepagents";

// TodoListMiddleware is included by default
const agent = await createDeepAgent({});

// Agent will automatically use write_todos for complex tasks
const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Create a TypeScript web scraper that extracts product data, stores it in a database, and generates a report."
  }]
});
```
</ex-default-config>

<ex-custom-config>
```typescript
import { createAgent, todoListMiddleware } from "langchain";

const agent = createAgent({
  model: "claude-sonnet-4-5-20250929",
  middleware: [
    todoListMiddleware({
      systemPrompt: `Use the write_todos tool to plan your work:
      1. Break down the task into 3-5 major steps
      2. Mark tasks as 'in_progress' when you start
      3. Mark tasks as 'completed' when done
      4. Update the list if plans change
      `,
    }),
  ],
});
```
</ex-custom-config>

<todo-patterns-table>
| Task Type | Todo List Strategy | Example |
|-----------|-------------------|---------|
| Sequential steps | Create all todos upfront, complete in order | Build app: setup -> code -> test -> deploy |
| Discovery-based | Add todos as you learn what's needed | Research: initial search -> follow-up -> synthesis |
| Parallel work | Multiple "in_progress" items allowed | Data processing: extract + transform + load |
</todo-patterns-table>

<ex-sequential-task>
```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: `Create a REST API for a todo application:
    1. Design the data models
    2. Implement CRUD endpoints
    3. Add authentication
    4. Write tests
    5. Create API documentation
    `
  }]
});

// Agent's internal planning (via write_todos):
// [
//   { content: "Design data models for Todo items", status: "pending" },
//   { content: "Implement CRUD endpoints (GET, POST, PUT, DELETE)", status: "pending" },
//   { content: "Add JWT authentication middleware", status: "pending" },
//   { content: "Write unit and integration tests", status: "pending" },
//   { content: "Generate OpenAPI documentation", status: "pending" }
// ]
```
</ex-sequential-task>

<ex-custom-instructions>
```typescript
import { createAgent, todoListMiddleware } from "langchain";
import { tool } from "langchain";
import { z } from "zod";

const runTests = tool(
  async ({ testSuite }: { testSuite: string }) => {
    return `Tests in ${testSuite} passed`;
  },
  {
    name: "run_tests",
    description: "Run a test suite",
    schema: z.object({ testSuite: z.string() }),
  }
);

const deployCode = tool(
  async ({ environment }: { environment: string }) => {
    return `Deployed to ${environment}`;
  },
  {
    name: "deploy_code",
    description: "Deploy code to an environment",
    schema: z.object({ environment: z.string() }),
  }
);

const agent = createAgent({
  model: "gpt-4",
  tools: [runTests, deployCode],
  middleware: [
    todoListMiddleware({
      systemPrompt: `For deployment tasks, always:
      1. Create a todo list with safety checks
      2. Run tests before deployment
      3. Mark each step as completed before proceeding
      `,
    }),
  ],
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Deploy the application to production"
  }]
});
```
</ex-custom-instructions>

<ex-accessing-todo-state>
```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});

const result = await agent.invoke(
  {
    messages: [{
      role: "user",
      content: "Create a data processing pipeline"
    }]
  },
  { configurable: { thread_id: "session-1" } }
);

// Access the todo list from the final state
const todos = result.todos || [];
for (const todo of todos) {
  console.log(`[${todo.status}] ${todo.content}`);
}
```
</ex-accessing-todo-state>

<boundaries>
**What Agents CAN Do with TodoLists**

- Create todo lists with custom content and structure
- Update todo status (pending -> in_progress -> completed)
- Add new todos as work progresses
- Remove todos that become irrelevant
- Reorganize or reprioritize todos
- Use todos for any task complexity level

**What Agents CANNOT Do**

- Change the tool name from `write_todos`
- Use custom status values (must be pending/in_progress/completed)
- Access todos from other threads without the thread_id
- Disable TodoListMiddleware in createDeepAgent (it's always included)
- Share todos across multiple agents (each agent has its own state)
</boundaries>

<fix-todolist-is-stateful>
```typescript
// WRONG: Todo list won't persist without thread_id
await agent.invoke({ messages: [{ role: "user", content: "Task 1" }] });
await agent.invoke({ messages: [{ role: "user", content: "Task 2" }] });

// CORRECT: Use thread_id for persistence
const config = { configurable: { thread_id: "user-session" } };
await agent.invoke({ messages: [{ role: "user", content: "Task 1" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "Task 2" }] }, config);
```
</fix-todolist-is-stateful>

<fix-middleware-always-present>
```typescript
// You cannot remove TodoListMiddleware from createDeepAgent
// WRONG: This won't remove TodoList
const agent = await createDeepAgent({ middleware: [] });  // TodoList still included

// CORRECT: If you need full control, use createAgent from LangChain
import { createAgent } from "langchain";

const agent2 = createAgent({
  model: "gpt-4",
  middleware: []  // No middleware at all
});
```
</fix-middleware-always-present>

<fix-todolist-is-optional>
```typescript
// The agent won't always use write_todos for simple tasks

// Simple task - agent likely won't create todos
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "What is 2+2?" }]
});
// No todos in state

// Complex task - agent will likely create todos
const result2 = await agent.invoke({
  messages: [{ role: "user", content: "Build a web scraper and analyze the data" }]
});
// Todos present in state
```
</fix-todolist-is-optional>

<documentation-links>
- [TodoList Middleware Guide](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/javascript/deepagents/harness)
- [TodoListMiddleware Reference](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#to-do-list)
</documentation-links>
