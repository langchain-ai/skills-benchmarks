Enable state persistence with checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

# Create checkpointer for state persistence
checkpointer = InMemorySaver()

# Compile with checkpointer
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue)
    .add_edge("tool_node", "llm_call")
    .compile(checkpointer=checkpointer)  # Add checkpointer
)

# First conversation turn
config = {"configurable": {"thread_id": "1"}}
agent.invoke(
    {"messages": [HumanMessage(content="Hi, I'm Alice")]},
    config
)

# Second turn - agent remembers context
agent.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config
)
```
