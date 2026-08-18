Dynamic model selection by task:

```python
from langchain.chat_models import init_chat_model

def get_model(task: str):
    model_map = {
        "reasoning": "openai:gpt-5",
        "fast": "google_genai:gemini-2.5-flash-lite",
        "vision": "openai:gpt-4.1",
        "long_context": "anthropic:claude-sonnet-4-5-20250929",
        "cost_effective": "openai:gpt-4.1-mini",
    }

    return init_chat_model(model_map.get(task, "openai:gpt-4.1"))

# Usage
reasoning_model = get_model("reasoning")
fast_model = get_model("fast")
```
