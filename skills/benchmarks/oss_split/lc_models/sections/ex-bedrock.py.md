AWS Bedrock setup:

```python
from langchain_aws import ChatBedrock

# AWS credentials from environment or ~/.aws/credentials
bedrock = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    # Credentials automatically loaded from environment
)
```
