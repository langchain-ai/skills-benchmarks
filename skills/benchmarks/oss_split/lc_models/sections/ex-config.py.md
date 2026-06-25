Configure model parameters:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4.1",

    # Control randomness (0 = deterministic, 1 = creative)
    temperature=0.7,

    # Limit response length
    max_tokens=500,

    # Alternative sampling method
    top_p=0.9,

    # Penalize repetition
    frequency_penalty=0.5,
    presence_penalty=0.5,

    # Stop generation at these strings
    stop=["\n\n", "END"],

    # Timeout for requests (seconds)
    request_timeout=30,

    # Max retries on failure
    max_retries=3,
)
```
