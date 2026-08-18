LangGraph for control, LangChain for simplicity:

```python
# LangChain (high-level, quick start)
from langchain.agents import create_agent
agent = create_agent(model, tools=[...])  # Simple, opinionated

# LangGraph (low-level, full control)
from langgraph.graph import StateGraph
graph = StateGraph(...).add_node(...).compile()  # More code, more control
```
