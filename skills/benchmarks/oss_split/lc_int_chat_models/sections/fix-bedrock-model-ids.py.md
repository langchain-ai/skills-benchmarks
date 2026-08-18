Use full Bedrock model ID format.

```python
# Wrong model ID format
model = ChatBedrock(model_id="claude-3-sonnet")  # Won't work!

# Correct: Full Bedrock model ID
model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)
```
