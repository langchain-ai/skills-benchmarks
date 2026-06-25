Mix deterministic and agentic steps:

```python
class HybridState(TypedDict):
    input: str
    validated: bool
    agent_response: str
    finalized: bool

def validate(state: HybridState) -> dict:
    """Fixed validation step."""
    return {"validated": True}

def agent_process(state: HybridState) -> dict:
    """Dynamic: agent decides how to process."""
    # Agent logic here
    response = f"Agent processed: {state['input']}"
    return {"agent_response": response}

def finalize(state: HybridState) -> dict:
    """Fixed finalization step."""
    return {"finalized": True}

# Hybrid: validate -> agent -> finalize
hybrid = (
    StateGraph(HybridState)
    .add_node("validate", validate)      # Workflow
    .add_node("agent", agent_process)    # Agent
    .add_node("finalize", finalize)      # Workflow
    .add_edge(START, "validate")
    .add_edge("validate", "agent")
    .add_edge("agent", "finalize")
    .add_edge("finalize", END)
    .compile()
)
```
