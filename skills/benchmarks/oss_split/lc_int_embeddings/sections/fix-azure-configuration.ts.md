Include all required Azure configuration fields.

```typescript
// Missing required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// All required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiEmbeddingsDeploymentName: "text-embedding-ada-002",
  azureOpenAIApiVersion: "2024-02-01",
});
```
