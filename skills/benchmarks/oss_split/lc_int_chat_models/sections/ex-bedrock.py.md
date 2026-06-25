Set up AWS Bedrock with Claude model.

```python
from langchain_aws import ChatBedrock
import boto3

model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1",
    credentials_profile_name="default",  # Or use boto3 session
)

response = model.invoke("What is AWS Bedrock?")
print(response.content)
```
