Complete Azure configuration with all fields.

```typescript
// INCOMPLETE: Missing required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// COMPLETE: All required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiDeploymentName: "gpt-4-deployment",
  azureOpenAIApiVersion: "2024-02-01",
});
```
