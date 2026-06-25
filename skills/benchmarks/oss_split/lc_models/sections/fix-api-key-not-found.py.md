Fix missing API key:

```python
# Problem: Missing API key
model = init_chat_model("openai:gpt-4.1")
model.invoke("Hello")  # Error: API key not found

# Solution: Set environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model("openai:gpt-4.1")

# OR pass directly
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="gpt-4.1",
    api_key="sk-...",
)
```
