Use provider built-in tools.

```python
from langchain_openai import ChatOpenAI

# OpenAI has built-in tools
model = ChatOpenAI(
    model="gpt-4.1",
    # Some models support built-in tools (check provider docs)
)

# Anthropic has built-in tools
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    # Provider-specific parameters
)
```
