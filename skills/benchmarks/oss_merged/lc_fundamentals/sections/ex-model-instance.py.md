Pass a model instance with custom settings instead of a model string.
```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
agent = create_agent(model=model, tools=[...])
```
