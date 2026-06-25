Stream tokens as they arrive:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
# Output appears progressively: "Quantum" "computing" "is" ...
```
