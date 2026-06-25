Batch process multiple inputs:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Process multiple inputs in parallel
results = model.batch([
    "What is AI?",
    "What is ML?",
    "What is LangChain?"
])

for i, result in enumerate(results):
    print(f"Answer {i + 1}: {result.content}")
```
