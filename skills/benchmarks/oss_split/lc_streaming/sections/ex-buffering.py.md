Buffer tokens for smoother UI updates:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

buffer = ""
for chunk in model.stream("Write a long essay"):
    buffer += chunk.content

    # Update UI every 10 characters or on complete words
    if len(buffer) >= 10 or " " in chunk.content:
        print(buffer, end="", flush=True)
        buffer = ""

# Flush remaining buffer
if buffer:
    print(buffer, end="", flush=True)
```
