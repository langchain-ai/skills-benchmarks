Add custom descriptions per tool:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4",
    tools=[deploy_tool, send_email_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "deploy_to_prod": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "PRODUCTION DEPLOYMENT requires approval"
                },
                "send_email": {
                    "description": "Email draft ready for review"
                },
            },
        ),
    ],
    checkpointer=MemorySaver(),
)
```
