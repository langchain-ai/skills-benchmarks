Tool-calling agent with routing:

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

# 1. Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# 2. Initialize model with tools
model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)
tools = [add, multiply]
model_with_tools = model.bind_tools(tools)

# 3. Define state
class MessagesState(TypedDict):
    messages: Annotated[list, operator.add]
    llm_calls: int

# 4. Define nodes
def llm_call(state: dict):
    """LLM decides whether to call a tool or not."""
    return {
        "messages": [
            model_with_tools.invoke([
                SystemMessage(content="You are a helpful assistant."),
                *state["messages"]
            ])
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Execute tool calls."""
    result = []
    tools_by_name = {tool.name: tool for tool in tools}
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# 5. Define routing logic
def should_continue(state: MessagesState):
    """Route to tool_node or END."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return END

# 6. Build and compile graph
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    .add_edge("tool_node", "llm_call")
    .compile()
)

# 7. Invoke the agent
messages = agent.invoke({"messages": [HumanMessage(content="What is 3 * 4?")]})
for m in messages["messages"]:
    m.pretty_print()
```
