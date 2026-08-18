Configure Azure OpenAI with deployment settings.

```python
from langchain_openai import AzureChatOpenAI
import os

model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4-deployment",
    api_version="2024-02-01",
    temperature=0.7,
)

response = model.invoke("Hello, how are you?")
print(response.content)
```
