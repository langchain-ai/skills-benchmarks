Choose models with sufficient context window.

```python
# Exceeding context limits
model = ChatOpenAI(model="gpt-3.5-turbo")  # 4k context
long_text = "..." * 10000
model.invoke(long_text)  # Will fail!

# Use appropriate models for long context
model = ChatOpenAI(model="gpt-4-turbo")  # 128k context
# OR
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229")  # 200k context
```
