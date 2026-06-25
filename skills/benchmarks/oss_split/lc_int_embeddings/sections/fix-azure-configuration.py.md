Include all required Azure configuration fields.

```python
# INCOMPLETE: Missing required fields
embeddings = AzureOpenAIEmbeddings(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# COMPLETE: All required fields
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint="https://my-instance.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="text-embedding-ada-002",
    api_version="2024-02-01",
)
```
