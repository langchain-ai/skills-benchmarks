Human approval for tool calls:

```python
from langgraph.types import interrupt, Command

def tool_executor(state):
    tool_calls = state["messages"][-1].tool_calls

    for tool_call in tool_calls:
        # Pause for each tool call
        user_decision = interrupt({
            "tool": tool_call["name"],
            "args": tool_call["args"],
            "question": "Execute this tool?"
        })

        if user_decision["type"] == "approve":
            # Execute tool
            result = execute_tool(tool_call)
        elif user_decision["type"] == "edit":
            # Use edited args
            result = execute_tool(user_decision["args"])
        else:  # reject
            result = "Tool execution rejected"

        # Store result
        results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    return {"messages": results}

# Usage
result = graph.invoke({"messages": [...]}, config)

# Review and approve
graph.invoke(Command(resume={"type": "approve"}), config)

# Or edit args
graph.invoke(
    Command(resume={"type": "edit", "args": {"query": "modified"}}),
    config
)

# Or reject
graph.invoke(Command(resume={"type": "reject"}), config)
```
