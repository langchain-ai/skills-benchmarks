Initialize Google Gemini model.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
import os

model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

response = model.invoke("Explain quantum computing")
print(response.content)
```
