Modify tool arguments before executing:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"execute_sql": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# Agent proposes SQL
result = agent.invoke({
    "messages": [{"role": "user", "content": "Delete old records from users table"}]
}, config=config)

# Get interrupt details
state = agent.get_state(config)
interrupt = state.tasks[0]
print(f"Proposed SQL: {interrupt.value['action_requests'][0]['args']}")

# Edit the SQL query
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{
                        "type": "edit",
                        "edited_action": {
                            "name": "execute_sql",
                            "args": {
                                "query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
                            }
                        }
                    }]
                }
            )
        ]
    }
)

# Continue with edited query
result = agent.invoke(None, config=config)
```
