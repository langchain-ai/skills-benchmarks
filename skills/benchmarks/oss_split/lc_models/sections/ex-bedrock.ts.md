AWS Bedrock setup:

```typescript
import { ChatBedrock } from "@langchain/aws";

// AWS credentials from environment or ~/.aws/credentials
const bedrock = new ChatBedrock({
  model: "anthropic.claude-3-5-sonnet-20240620-v1:0",
  region: "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});
```
