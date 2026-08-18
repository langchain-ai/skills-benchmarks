Chain researcher and analyst subagents:

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web."""
    return f"Search results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze data and extract insights."""
    return f"Analysis: {data[:100]}..."

agent = create_deep_agent(
    subagents=[
        {
            "name": "researcher",
            "description": "Conduct web research and compile findings",
            "system_prompt": "Search thoroughly, save results to /research/ directory, return concise summary",
            "tools": [web_search],
        },
        {
            "name": "analyst",
            "description": "Analyze data and provide insights",
            "system_prompt": "Provide data-driven insights with specific numbers",
            "tools": [analyze_data],
        }
    ]
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Research market trends for EVs, then analyze the data"
    }]
})
# Main agent: task(agent="researcher", ...) -> task(agent="analyst", ...)
```
