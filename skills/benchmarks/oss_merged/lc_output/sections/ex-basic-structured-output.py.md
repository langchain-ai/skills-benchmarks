Extract contact information from text using a Pydantic schema with email validation.
```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    phone: str

agent = create_agent(model="gpt-4.1", response_format=ContactInfo)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract: John Doe, john@example.com, (555) 123-4567"}]
})
print(result["structured_response"])
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```
