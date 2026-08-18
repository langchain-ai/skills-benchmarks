Use GPT-4 or similar for tool calling.

```python
# Model doesn't support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This model doesn't support tools!

# Use tool-capable model
model = ChatOpenAI(model="gpt-4")
```
