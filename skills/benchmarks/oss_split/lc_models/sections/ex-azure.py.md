Azure OpenAI setup:

```python
from langchain_openai import AzureChatOpenAI
import os

azure = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    deployment_name="your-deployment-name",
)
```
