Specify model by string or instance:

```python
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

# Use provider:model format
agent = create_deep_agent(
    model="openai:gpt-4"
)

# Or pass a model instance
model = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_deep_agent(
    model=model
)
```
