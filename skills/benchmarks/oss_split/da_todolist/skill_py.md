---
name: Deep Agents Todo List (Python)
description: [Deep Agents] Using TodoListMiddleware for task planning and tracking progress with the write_todos tool in Deep Agents for complex multi-step workflows.
---

<overview>
TodoListMiddleware provides agents with task planning and progress tracking capabilities through the `write_todos` tool. It's automatically included in every deep agent and helps agents break down complex, multi-step tasks into manageable pieces.

Planning is integral to solving complex problems. The middleware enables agents to:
- Break down complex tasks into discrete steps
- Track progress as tasks are completed
- Adapt plans dynamically as new information emerges
- Provide visibility into long-running operations
</overview>

<when-to-use-todolist>
| Use TodoList When | Skip TodoList When |
|------------------|-------------------|
| Complex multi-step tasks requiring coordination | Simple, single-action tasks |
| Long-running operations where progress visibility matters | Quick operations (< 3 steps) |
| Tasks that may need plan adaptation | Fixed, predetermined workflows |
| Multiple tools need to be orchestrated | Single tool invocation |
</when-to-use-todolist>

<how-it-works>
TodoListMiddleware is automatically included in `create_deep_agent()`. The agent receives:

1. A `write_todos` tool for managing the task list
2. System prompt instructions on when and how to use planning
3. State persistence for the todo list across agent steps

### The write_todos Tool

```python
write_todos(todos: list[dict]) -> None
```

Each todo item has:
- `content`: Description of the task
- `status`: One of `"pending"`, `"in_progress"`, `"completed"`
</how-it-works>

<ex-default-configuration>
```python
from deepagents import create_deep_agent

# TodoListMiddleware is included by default
agent = create_deep_agent()

# Agent will automatically use write_todos for complex tasks
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Create a Python web scraper that extracts product data from an e-commerce site, stores it in a database, and generates a report."
    }]
})
```
</ex-default-configuration>

<ex-customizing-todolist-middleware>
```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

# Custom agent with customized TodoList behavior
agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        TodoListMiddleware(
            system_prompt="""Use the write_todos tool to plan your work:
            1. Break down the task into 3-5 major steps
            2. Mark tasks as 'in_progress' when you start
            3. Mark tasks as 'completed' when done
            4. Update the list if plans change
            """,
            tool_description="Manage your task list for complex multi-step work"
        ),
    ],
)
```
</ex-customizing-todolist-middleware>

<todolist-patterns>
| Task Type | Todo List Strategy | Example |
|-----------|-------------------|---------|
| Sequential steps | Create all todos upfront, complete in order | Build app: setup -> code -> test -> deploy |
| Discovery-based | Add todos as you learn what's needed | Research: initial search -> follow-up -> synthesis |
| Parallel work | Multiple "in_progress" items allowed | Data processing: extract + transform + load |
| Iterative refinement | Update todo content as you refine approach | Debugging: reproduce -> isolate -> fix -> verify |
</todolist-patterns>

<ex-sequential-task-breakdown>
```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# The agent will use write_todos to plan this multi-step task
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": """Create a REST API for a todo application:
        1. Design the data models
        2. Implement CRUD endpoints
        3. Add authentication
        4. Write tests
        5. Create API documentation
        """
    }]
})

# Agent's internal planning (via write_todos):
# [
#   {"content": "Design data models for Todo items", "status": "pending"},
#   {"content": "Implement CRUD endpoints (GET, POST, PUT, DELETE)", "status": "pending"},
#   {"content": "Add JWT authentication middleware", "status": "pending"},
#   {"content": "Write unit and integration tests", "status": "pending"},
#   {"content": "Generate OpenAPI documentation", "status": "pending"}
# ]
```
</ex-sequential-task-breakdown>

<ex-adaptive-planning>
```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Complex task where requirements emerge over time
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Debug why the application crashes on startup"
    }]
})

# Agent's evolving plan:
# Initial todos:
# [
#   {"content": "Reproduce the crash", "status": "in_progress"},
#   {"content": "Check error logs", "status": "pending"},
#   {"content": "Identify root cause", "status": "pending"}
# ]
#
# After investigation, agent updates:
# [
#   {"content": "Reproduce the crash", "status": "completed"},
#   {"content": "Check error logs", "status": "completed"},
#   {"content": "Identified missing environment variable", "status": "completed"},
#   {"content": "Add environment variable validation on startup", "status": "in_progress"},
#   {"content": "Update deployment documentation", "status": "pending"}
# ]
```
</ex-adaptive-planning>

<ex-custom-todolist-instructions>
```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool

@tool
def run_tests(test_suite: str) -> str:
    """Run a test suite."""
    return f"Tests in {test_suite} passed"

@tool
def deploy_code(environment: str) -> str:
    """Deploy code to an environment."""
    return f"Deployed to {environment}"

agent = create_agent(
    model="gpt-4",
    tools=[run_tests, deploy_code],
    middleware=[
        TodoListMiddleware(
            system_prompt="""For deployment tasks, always:
            1. Create a todo list with safety checks
            2. Run tests before deployment
            3. Mark each step as completed before proceeding
            """,
        ),
    ],
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Deploy the application to production"
    }]
})
```
</ex-custom-todolist-instructions>

<ex-accessing-todo-state>
```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Run the agent
result = agent.invoke(
    {
        "messages": [{
            "role": "user",
            "content": "Create a data processing pipeline"
        }]
    },
    config={"configurable": {"thread_id": "session-1"}}
)

# Access the todo list from the final state
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['content']}")
```
</ex-accessing-todo-state>

<boundaries>
### What Agents CAN Do with TodoLists

- Create todo lists with custom content and structure
- Update todo status (pending -> in_progress -> completed)
- Add new todos as work progresses
- Remove todos that become irrelevant
- Reorganize or reprioritize todos
- Use todos for any task complexity level

### What Agents CANNOT Do

- Change the tool name from `write_todos`
- Use custom status values (must be pending/in_progress/completed)
- Access todos from other threads without the thread_id
- Disable TodoListMiddleware in create_deep_agent (it's always included)
- Share todos across multiple agents (each agent has its own state)
</boundaries>

<fix-todolist-requires-thread-id>
```python
# WRONG: Todo list won't persist without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Task 1"}]})
agent.invoke({"messages": [{"role": "user", "content": "Task 2"}]})

# CORRECT: Use thread_id for persistence
config = {"configurable": {"thread_id": "user-session"}}
agent.invoke({"messages": [{"role": "user", "content": "Task 1"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "Task 2"}]}, config=config)
```
</fix-todolist-requires-thread-id>

<fix-todolist-always-present>
```python
# You cannot remove TodoListMiddleware from create_deep_agent
# It's part of the core harness

# WRONG: This won't remove TodoList
from deepagents import create_deep_agent

agent = create_deep_agent(middleware=[])  # TodoList still included

# CORRECT: If you need full control, use create_agent from LangChain
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4",
    middleware=[]  # No middleware at all
)
```
</fix-todolist-always-present>

<fix-todos-not-shared-across-agents>
```python
# WRONG: Subagents have their own todo lists
from deepagents import create_deep_agent

main_agent = create_deep_agent()
result = main_agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Use a subagent to process data"
    }]
})

# The subagent's todos are separate and won't appear in main_agent's state
```
</fix-todos-not-shared-across-agents>

<fix-todolist-optional-for-simple-tasks>
```python
# The agent won't always use write_todos
# For simple tasks, it may skip planning

from deepagents import create_deep_agent

agent = create_deep_agent()

# Simple task - agent likely won't create todos
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is 2+2?"}]
})
# No todos in state

# Complex task - agent will likely create todos
result = agent.invoke({
    "messages": [{"role": "user", "content": "Build a web scraper and analyze the data"}]
})
# Todos present in state
```
</fix-todolist-optional-for-simple-tasks>

<links>
- [TodoList Middleware Guide](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/python/deepagents/harness)
- [TodoListMiddleware API Reference](https://docs.langchain.com/oss/python/langchain/middleware/built-in#to-do-list)
</links>
