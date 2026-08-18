Analyze PDF document with Claude.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import base64

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

with open("./document.pdf", "rb") as pdf_file:
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Summarize this PDF document"},
    {
        "type": "file",
        "base64": base64_pdf,
        "mime_type": "application/pdf",
    },
])

response = model.invoke([message])
```
