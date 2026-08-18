Check model supports tool calling.

```python
# Not all models support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This older model doesn't support tools!

# Use models with tool support
model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([my_tool])
```
