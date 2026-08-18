Offload search results to filesystem:

```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Agent offloads search results to filesystem
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Search for information about Python asyncio and save the results for later analysis"
    }]
})

# Agent workflow:
# 1. Use search tool -> large results
# 2. write_file("/search-results.txt", results)
# 3. Continue with compact context
# 4. Later: read_file("/search-results.txt") when needed
```
