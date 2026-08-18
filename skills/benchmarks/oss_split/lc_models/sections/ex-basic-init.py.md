Universal model initialization:

```python
from langchain.chat_models import init_chat_model

# Universal initialization - easiest way
model = init_chat_model("openai:gpt-4.1")

# Or with provider shorthand
model2 = init_chat_model("gpt-4.1")  # Defaults to OpenAI

# API key from environment (recommended)
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
model3 = init_chat_model("openai:gpt-4.1")
```
