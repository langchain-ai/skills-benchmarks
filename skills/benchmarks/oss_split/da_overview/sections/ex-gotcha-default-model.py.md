Set API key for default model:

```python
# Uses claude-sonnet-4-5-20250929 by default
agent = create_deep_agent()

# Requires ANTHROPIC_API_KEY environment variable
# Set OPENAI_API_KEY if using OpenAI models
import os
os.environ["ANTHROPIC_API_KEY"] = "your-key"
```
