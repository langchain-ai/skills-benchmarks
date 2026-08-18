Use environment variables for API keys.

```python
# BAD: Hardcoding API keys
model = ChatOpenAI(
    api_key="sk-..."  # Never commit this!
)

# GOOD: Use environment variables
import os
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# BETTER: Let LangChain auto-detect from environment
model = ChatOpenAI()  # Reads OPENAI_API_KEY automatically
```
