Switch from text-only to vision-capable model.

```python
# Problem: Using text-only model
model = ChatOpenAI(model="gpt-3.5-turbo")
model.invoke([image_message])  # Error!

# Solution: Use vision-capable model
model = ChatOpenAI(model="gpt-4.1")
```
