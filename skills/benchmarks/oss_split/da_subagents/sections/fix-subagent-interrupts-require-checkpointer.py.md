Add checkpointer to main agent:

```python
# Subagent HITL without checkpointer
agent = create_deep_agent(
    subagents=[{
        "name": "deployer",
        "interrupt_on": {"deploy": True}
    }]
)

# Checkpointer on main agent, not subagent
agent = create_deep_agent(
    subagents=[{
        "name": "deployer",
        "interrupt_on": {"deploy": True}
    }],
    checkpointer=MemorySaver()  # On main agent
)
```
