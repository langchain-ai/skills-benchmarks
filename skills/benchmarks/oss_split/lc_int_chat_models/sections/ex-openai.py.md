Initialize OpenAI chat model and stream responses.

```python
from langchain_openai import ChatOpenAI
import os

# Basic initialization
model = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),  # Optional if set in env
)

# Invoke the model
response = model.invoke([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is LangChain?"}
])

print(response.content)

# Streaming responses
for chunk in model.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```
