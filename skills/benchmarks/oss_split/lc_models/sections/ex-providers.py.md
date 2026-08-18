Provider-specific class initialization:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# OpenAI
openai = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7,
    max_tokens=1000,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Anthropic
anthropic = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0,
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Google
google = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
```
