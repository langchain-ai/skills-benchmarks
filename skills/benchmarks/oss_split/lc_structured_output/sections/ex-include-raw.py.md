Get both raw message and parsed output.

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

model = ChatOpenAI(model="gpt-4.1")
structured_model = model.with_structured_output(Person, include_raw=True)

response = structured_model.invoke("Person: Alice, 30 years old")
print(response)
# {
#   "raw": AIMessage(...),
#   "parsed": Person(name="Alice", age=30)
# }
```
