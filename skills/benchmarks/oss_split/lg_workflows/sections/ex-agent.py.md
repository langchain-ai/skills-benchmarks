Tool-calling agent with dynamic routing:

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def calculate(a: float, b: float, op: str) -> str:
    """Calculate a mathematical expression.

    Args:
        a: First number
        b: Second number
        op: Operation (add, subtract, multiply, divide)
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return str(ops.get(op, "Invalid operation"))

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

model = init_chat_model("claude-sonnet-4-5-20250929")
tools = [search, calculate]
model_with_tools = model.bind_tools(tools)

def agent_node(state: AgentState) -> dict:
    """Agent decides which tool to use (if any)."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute tools chosen by agent."""
    tools_by_name = {tool.name: tool for tool in tools}
    result = []

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: AgentState):
    """Dynamic: agent decides if it needs more tools."""
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# Dynamic agent: model decides when to stop
agent = (
    StateGraph(AgentState)
    .add_node("agent", agent_node)
    .add_node("tools", tool_node)
    .add_edge(START, "agent")
    .add_conditional_edges("agent", should_continue)  # Model decides
    .add_edge("tools", "agent")
    .compile()
)
```
