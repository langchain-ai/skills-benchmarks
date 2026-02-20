---
name: Deep Agents Orchestration (Python)
description: "INVOKE THIS SKILL when using subagents, task planning, or human approval in Deep Agents. Covers SubAgentMiddleware, TodoList for planning, and HITL interrupts. CRITICAL: Fixes for custom subagents NOT inheriting skills (must specify explicitly), interrupt_on requiring checkpointer, and subagent statelessness."
---

<overview>
Deep Agents include three orchestration capabilities:

1. **SubAgentMiddleware**: Delegate work via `task` tool to specialized agents
2. **TodoListMiddleware**: Plan and track tasks via `write_todos` tool
3. **HumanInTheLoopMiddleware**: Require approval before sensitive operations

All three are automatically included in `create_deep_agent()`.
</overview>

---

## Subagents (Task Delegation)

<when-to-use-subagents>

| Use Subagents When | Use Main Agent When |
|-------------------|-------------------|
| Task needs specialized tools | General-purpose tools sufficient |
| Want to isolate complex multi-step work | Single-step operation |
| Need clean context for main agent | Context bloat acceptable |
| Task benefits from different model/prompt | Same config works |

</when-to-use-subagents>

<how-subagents-work>
Main agent has `task` tool -> creates fresh subagent -> subagent executes autonomously -> returns final report.

**Default subagent**: "general-purpose" - automatically available with same tools/config as main agent.
</how-subagents-work>

<ex-custom-subagents>
```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def search_papers(query: str) -> str:
    """Search academic papers."""
    return f"Found 10 papers about {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze data and extract insights."""
    return f"Analysis: {data[:100]}..."

agent = create_deep_agent(
    subagents=[
        {
            "name": "researcher",
            "description": "Conduct web research and compile findings",
            "system_prompt": "Search thoroughly, save results to /research/, return concise summary",
            "tools": [search_papers],
            "model": "claude-sonnet-4-5-20250929",  # Optional override
        },
        {
            "name": "analyst",
            "description": "Analyze data and provide insights",
            "tools": [analyze_data],
        }
    ]
)

# Main agent delegates: task(agent="researcher", instruction="Research AI trends")
```
</ex-custom-subagents>

<ex-subagent-with-hitl>
```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    subagents=[
        {
            "name": "code-deployer",
            "description": "Deploy code to production",
            "tools": [run_tests, deploy_to_prod],
            "interrupt_on": {"deploy_to_prod": True},  # Require approval
        }
    ],
    checkpointer=MemorySaver()  # Required for interrupts
)
```
</ex-subagent-with-hitl>

<fix-subagents-are-stateless>
```python
# WRONG: Subagents don't remember previous calls
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='Find data')"}]})
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='What did you find?')"}]})
# Second call starts fresh - subagent doesn't remember first call

# CORRECT: Provide complete instructions upfront
# task(agent='research', instruction='Find data on AI, save to /research/, return summary')
```
</fix-subagents-are-stateless>

<fix-custom-subagents-dont-inherit-skills>
```python
# WRONG: Custom subagent won't have main agent's skills
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills inherited
)

# CORRECT: Explicitly provide skills to custom subagent
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Explicit
        ...
    }]
)

# Note: General-purpose subagent DOES inherit main skills
```
</fix-custom-subagents-dont-inherit-skills>

---

## TodoList (Task Planning)

<when-to-use-todolist>

| Use TodoList When | Skip TodoList When |
|------------------|-------------------|
| Complex multi-step tasks | Simple single-action tasks |
| Long-running operations | Quick operations (< 3 steps) |
| Tasks needing plan adaptation | Fixed predetermined workflows |

</when-to-use-todolist>

<todolist-tool>
```python
write_todos(todos: list[dict]) -> None
```

Each todo item has:
- `content`: Description of the task
- `status`: One of `"pending"`, `"in_progress"`, `"completed"`
</todolist-tool>

<ex-todolist-usage>
```python
from deepagents import create_deep_agent

# TodoListMiddleware included by default
agent = create_deep_agent()

# Agent will use write_todos for complex tasks
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Create a REST API: design models, implement CRUD, add auth, write tests"
    }]
}, config={"configurable": {"thread_id": "session-1"}})

# Agent's internal planning (via write_todos):
# [
#   {"content": "Design data models", "status": "in_progress"},
#   {"content": "Implement CRUD endpoints", "status": "pending"},
#   {"content": "Add authentication", "status": "pending"},
#   {"content": "Write tests", "status": "pending"}
# ]
```
</ex-todolist-usage>

<ex-access-todo-state>
```python
result = agent.invoke({...}, config={"configurable": {"thread_id": "session-1"}})

# Access todo list from final state
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['content']}")
```
</ex-access-todo-state>

<fix-todolist-requires-thread-id>
```python
# WRONG: Todo list won't persist without thread_id
agent.invoke({"messages": [...]})
agent.invoke({"messages": [...]})  # Fresh state each time

# CORRECT: Use thread_id for persistence
config = {"configurable": {"thread_id": "user-session"}}
agent.invoke({"messages": [...]}, config=config)
agent.invoke({"messages": [...]}, config=config)  # Todos preserved
```
</fix-todolist-requires-thread-id>

---

## Human-in-the-Loop (Approval Workflows)

<when-to-use-hitl>

| Use HITL When | Skip HITL When |
|--------------|---------------|
| High-stakes operations (DB writes, deployments) | Read-only operations |
| Compliance requires human oversight | Fully automated workflows |
| Expensive API calls need verification | Low-cost operations |

</when-to-use-hitl>

<interrupt-strategies>

| Tool Type | Interrupt Config | Allowed Decisions |
|-----------|-----------------|------------------|
| Destructive | `True` | approve, edit, reject |
| Critical | `{"allowed_decisions": ["approve", "reject"]}` | approve, reject only |
| Safe | `False` | none (no interrupt) |

</interrupt-strategies>

<ex-hitl-setup>
```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={
        "write_file": True,  # All decisions allowed
        "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # No editing
        "read_file": False,  # No interrupts
    },
    checkpointer=MemorySaver()  # REQUIRED for interrupts
)
```
</ex-hitl-setup>

<ex-approval-workflow>
```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import Command

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent proposes write_file - execution pauses
result = agent.invoke({
    "messages": [{"role": "user", "content": "Write config to /prod.yaml"}]
}, config=config)

# Step 2: Check for interrupts
state = agent.get_state(config)
if state.next:  # Has interrupts
    interrupt = state.tasks[0]
    print(f"Pending: {interrupt}")

# Step 3: Approve the action
agent.update_state(
    config,
    {"messages": [Command(resume={"decisions": [{"type": "approve"}]})]}
)

# Step 4: Resume execution
result = agent.invoke(None, config=config)
```
</ex-approval-workflow>

<ex-reject-with-feedback>
```python
# Reject and provide feedback
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "reject",
                        "message": "Tests haven't passed yet. Run tests first."
                    }]
                }
            )
        ]
    }
)

# Agent receives rejection feedback and can try alternative approach
result = agent.invoke(None, config=config)
```
</ex-reject-with-feedback>

<ex-edit-before-execution>
```python
# Edit the proposed action
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "edit",
                        "args": {
                            "query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
                        }
                    }]
                }
            )
        ]
    }
)

result = agent.invoke(None, config=config)
```
</ex-edit-before-execution>

<fix-checkpointer-required>
```python
# WRONG: This will error - checkpointer required for interrupts
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# CORRECT: Must provide checkpointer
agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
</fix-checkpointer-required>

<fix-thread-id-required-for-resumption>
```python
# WRONG: Can't resume without thread_id
agent.invoke({"messages": [...]})
agent.update_state(...)  # Which thread?

# CORRECT: Use consistent thread_id
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
agent.update_state(config, ...)
agent.invoke(None, config=config)  # Resume
```
</fix-thread-id-required-for-resumption>

<fix-interrupt-checks-between-invocations>
```python
# Interrupts happen BETWEEN invoke() calls, not mid-execution

# Step 1: invoke() -> interrupt triggers
result = agent.invoke({...}, config=config)

# Step 2: Check state for interrupts
state = agent.get_state(config)
if state.next:  # Has pending interrupts
    # Handle them

# Step 3: Resume
agent.update_state(config, {...})
result = agent.invoke(None, config=config)
```
</fix-interrupt-checks-between-invocations>

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
- Share state directly between subagents
</boundaries>
