**What Agents CAN Do with TodoLists:**
- Create todo lists with custom content and structure
- Update todo status (pending -> in_progress -> completed)
- Add new todos as work progresses
- Remove todos that become irrelevant
- Reorganize or reprioritize todos
- Use todos for any task complexity level

**What Agents CANNOT Do:**
- Change the tool name from `write_todos`
- Use custom status values (must be pending/in_progress/completed)
- Access todos from other threads without the thread_id
- Disable TodoListMiddleware in create_deep_agent/createDeepAgent (it's always included)
- Share todos across multiple agents (each agent has its own state)
