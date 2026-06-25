Handle API errors:

```python
from langchain.chat_models import init_chat_model
from openai import RateLimitError, AuthenticationError

model = init_chat_model("gpt-4.1")

try:
    response = model.invoke("Hello!")
    print(response.content)
except RateLimitError:
    print("Rate limit exceeded")
except AuthenticationError:
    print("Invalid API key")
except Exception as e:
    print(f"Error: {e}")
```
