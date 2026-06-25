Use TypedDict for simpler dict output.

```python
from typing_extensions import TypedDict, Annotated
from langchain.agents import create_agent

class ContactDict(TypedDict):
    """Contact information."""
    name: Annotated[str, ..., "Person's full name"]
    email: Annotated[str, ..., "Email address"]
    phone: Annotated[str, ..., "Phone number"]

agent = create_agent(
    model="gpt-4.1",
    response_format=ContactDict,
)

result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
# Returns dict, not Pydantic model
print(type(result["structured_response"]))  # <class 'dict'>
```
