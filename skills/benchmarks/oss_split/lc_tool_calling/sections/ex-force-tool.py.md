Force model to use a specific tool.

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str

@tool
def extract_info(name: str, email: str) -> dict:
    """Extract name and email.

    Args:
        name: Person's name
        email: Email address
    """
    return {"name": name, "email": email}

model = ChatOpenAI(model="gpt-4.1")

# Force model to use this specific tool
model_with_tools = model.bind_tools(
    [extract_info],
    tool_choice="extract_info"  # Must use this tool
)

response = model_with_tools.invoke("Contact: John Doe (john@example.com)")

# Model always calls extract_info
print(response.tool_calls[0]["args"])
# {'name': 'John Doe', 'email': 'john@example.com'}
```
