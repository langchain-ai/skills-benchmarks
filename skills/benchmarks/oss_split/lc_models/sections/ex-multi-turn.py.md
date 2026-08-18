Multi-turn conversation with history:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Build conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
]

response1 = model.invoke(messages)
messages.append({"role": "assistant", "content": response1.content})

# Continue conversation
messages.append({"role": "user", "content": "What's its population?"})
response2 = model.invoke(messages)

print(response2.content)  # Knows we're talking about Paris
```
