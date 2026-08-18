Stream tokens in real-time:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```
