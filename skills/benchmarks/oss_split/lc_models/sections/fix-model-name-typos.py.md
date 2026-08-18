Fix model name format:

```python
# Problem: Wrong model name
model = init_chat_model("gpt4")  # Error!

# Solution: Use correct format
model = init_chat_model("openai:gpt-4.1")
# Or provider shorthand
model2 = init_chat_model("gpt-4.1")
```
