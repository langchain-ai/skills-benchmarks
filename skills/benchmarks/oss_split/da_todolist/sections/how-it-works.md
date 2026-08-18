TodoListMiddleware is automatically included in `create_deep_agent()` / `createDeepAgent()`. The agent receives:

1. A `write_todos` tool for managing the task list
2. System prompt instructions on when and how to use planning
3. State persistence for the todo list across agent steps

### The write_todos Tool

Each todo item has:
- `content`: Description of the task
- `status`: One of `"pending"`, `"in_progress"`, `"completed"`
