Dict and message class formats both work.

```python
# Different message formats that all work
from langchain_core.messages import HumanMessage, SystemMessage

# Dictionary format
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"}
]

# Message class format
messages = [
    SystemMessage(content="You are helpful"),
    HumanMessage(content="Hello")
]

# Both work!
response = model.invoke(messages)
```
