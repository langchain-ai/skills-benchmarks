Azure OpenAI setup:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const azure = new ChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "your-instance-name",
  azureOpenAIApiDeploymentName: "your-deployment-name",
  azureOpenAIApiVersion: "2024-02-15-preview",
});
```
