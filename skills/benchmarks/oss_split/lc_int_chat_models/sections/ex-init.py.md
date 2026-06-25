Provider-agnostic model initialization.

```python
from langchain.chat_models import init_chat_model

# Automatically select model based on environment
model = init_chat_model(
    "gpt-4",
    model_provider="openai",
    temperature=0.7,
)

# Or with Bedrock
bedrock_model = init_chat_model(
    "anthropic.claude-3-sonnet-20240229-v1:0",
    model_provider="bedrock",
)
```
