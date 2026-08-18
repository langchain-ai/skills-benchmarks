Use default subagent for context isolation:

```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Agent can use default "general-purpose" subagent for context isolation
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Analyze this large dataset and summarize the key findings"
    }]
})
# Agent may call: task(instruction="Analyze dataset and summarize")
# Uses general-purpose subagent with same tools/config as main
```
