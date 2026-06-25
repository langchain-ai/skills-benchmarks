Extract data from chart image with Claude.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

message = HumanMessage(content_blocks=[
    {"type": "image", "url": "https://example.com/chart.png"},
    {"type": "text", "text": "Extract all data points from this chart"},
])

response = model.invoke([message])
```
