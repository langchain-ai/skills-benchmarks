Async invoke, stream, and batch:

```python
from langchain.chat_models import init_chat_model
import asyncio

async def main():
    model = init_chat_model("gpt-4.1")

    # Async invoke
    response = await model.ainvoke("Hello!")
    print(response.content)

    # Async stream
    async for chunk in model.astream("Explain AI"):
        print(chunk.content, end="", flush=True)

    # Async batch
    results = await model.abatch([
        "What is AI?",
        "What is ML?",
    ])
    for result in results:
        print(result.content)

asyncio.run(main())
```
