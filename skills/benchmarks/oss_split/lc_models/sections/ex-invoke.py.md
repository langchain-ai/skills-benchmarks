Basic invoke with string and messages:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# String input (converted to HumanMessage)
response = model.invoke("What is LangChain?")
print(response.content)

# Message array input
response2 = model.invoke([
    {"role": "user", "content": "Hello!"}
])
print(response2.content)
```
