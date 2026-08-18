Use async methods in async context:

```python
# Problem: Using sync in async context
async def process():
    model = init_chat_model("gpt-4.1")
    response = model.invoke("Hello")  # Blocks async loop!

# Solution: Use async methods
async def process():
    model = init_chat_model("gpt-4.1")
    response = await model.ainvoke("Hello")  # Non-blocking

    async for chunk in model.astream("Hello"):
        print(chunk.content)
```
