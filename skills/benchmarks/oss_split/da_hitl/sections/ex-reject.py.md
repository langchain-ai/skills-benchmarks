Reject and provide feedback to agent:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"deploy_code": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

result = agent.invoke({
    "messages": [{"role": "user", "content": "Deploy to production"}]
}, config=config)

# Reject deployment
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
