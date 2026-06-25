Combine multiple tools in one agent.

```python
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain.agents import create_agent

# Define tools
search_tool = TavilySearchResults(max_results=3)

@tool
def calculator(a: float, b: float, op: str) -> str:
    """Perform a mathematical operation.

    Args:
        a: First number
        b: Second number
        op: Operation to perform (add, subtract, multiply, divide)
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else float('inf')}
    result = ops.get(op)
    if result is None:
        return f"Error: Unknown operation '{op}'"
    return str(result)

@tool
def custom_lookup(query: str) -> str:
    """Look up custom information.

    Args:
        query: The query to look up
    """
    # Your custom logic
    return f"Custom result for: {query}"

# Create agent with multiple tools
agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool, calculator, custom_lookup],
)

# Agent will choose appropriate tool(s)
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Search for the population of Tokyo and calculate if it doubled"
    }]
})
```
