Use provider-specific packages for imports.

```python
# WRONG: Using old community package
from langchain.chat_models import ChatOpenAI  # Deprecated!

# CORRECT: Use provider-specific package
from langchain_openai import ChatOpenAI
```
