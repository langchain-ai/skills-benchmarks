Check model capabilities:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Check if model supports features
print("Supports streaming:", hasattr(model, "stream"))
print("Supports tool calling:", hasattr(model, "bind_tools"))
print("Supports structured output:", hasattr(model, "with_structured_output"))
```
