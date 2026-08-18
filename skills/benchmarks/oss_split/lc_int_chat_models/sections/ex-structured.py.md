Generate structured output with Pydantic schema.

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

class Person(BaseModel):
    name: str = Field(description="Person's name")
    age: int = Field(description="Person's age")
    hobbies: List[str] = Field(description="List of hobbies")

model = ChatOpenAI(model="gpt-4")
structured_model = model.with_structured_output(Person)

response = structured_model.invoke(
    "Tell me about a person named Alice who is 30 years old and likes reading"
)
print(response)  # Returns Person object
print(f"Name: {response.name}, Age: {response.age}")
```
