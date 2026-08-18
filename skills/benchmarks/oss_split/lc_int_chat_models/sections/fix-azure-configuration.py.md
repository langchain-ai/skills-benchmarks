Updated Azure configuration syntax.

```python
# OLD WAY (deprecated)
from langchain_openai import AzureChatOpenAI
model = AzureChatOpenAI(
    deployment_name="gpt-4",
    openai_api_base="https://my-instance.openai.azure.com/",
)

# NEW WAY
model = AzureChatOpenAI(
    azure_endpoint="https://my-instance.openai.azure.com/",
    azure_deployment="gpt-4",
    api_version="2024-02-01",
)
```
