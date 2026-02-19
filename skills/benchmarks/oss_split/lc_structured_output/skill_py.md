---
name: LangChain Structured Output (Python)
description: "[LangChain] Get structured, validated output from LangChain agents and models using Pydantic schemas, type-safe responses, and automatic validation"
---

<overview>
Structured output transforms unstructured model responses into validated, typed data. Instead of parsing free text, you get Python objects conforming to your schema - perfect for extracting data, building forms, or integrating with downstream systems.

**Key Concepts:**
- **response_format**: Define expected output schema
- **Pydantic Validation**: Type-safe schemas with automatic validation
- **with_structured_output()**: Model method for direct structured output
- **Tool Strategy**: Uses tool calling under the hood for models without native support
</overview>

<when-to-use-structured-output>

| Use Case | Use Structured Output? | Why |
|----------|----------------------|-----|
| Extract contact info, dates, etc. | Yes | Reliable data extraction |
| Form filling | Yes | Validate all required fields |
| API integration | Yes | Type-safe responses |
| Classification tasks | Yes | Enum validation |
| Open-ended Q&A | No | Free-form text is fine |
| Creative writing | No | Don't constrain creativity |

</when-to-use-structured-output>

<schema-options>

| Schema Type | When to Use | Example |
|-------------|-------------|---------|
| Pydantic model | Python projects (recommended) | `class Model(BaseModel):` |
| TypedDict | Simpler typing | `class Data(TypedDict):` |
| JSON Schema | Interoperability | `{"type": "object", ...}` |
| Union types | Multiple possible formats | `Union[Schema1, Schema2]` |

</schema-options>

<ex-basic-structured-output-with-agent>
```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    phone: str

agent = create_agent(
    model="gpt-4.1",
    response_format=ContactInfo,
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Extract: John Doe, john@example.com, (555) 123-4567"
    }]
})

print(result["structured_response"])
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```
</ex-basic-structured-output-with-agent>

<ex-model-direct-structured-output>
```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """Movie information."""
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    director: str
    rating: float = Field(ge=0, le=10)

model = ChatOpenAI(model="gpt-4.1")
structured_model = model.with_structured_output(Movie)

response = structured_model.invoke("Tell me about Inception")
print(response)
# Movie(title="Inception", year=2010, director="Christopher Nolan", rating=8.8)
```
</ex-model-direct-structured-output>

<ex-complex-nested-schema>
```python
from pydantic import BaseModel, Field
from typing import List

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str

class Person(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str
    address: Address
    tags: List[str] = Field(default_factory=list)

agent = create_agent(
    model="gpt-4.1",
    response_format=Person,
)
```
</ex-complex-nested-schema>

<ex-enum-and-literal-types>
```python
from pydantic import BaseModel, Field
from typing import Literal

class Classification(BaseModel):
    category: Literal["urgent", "normal", "low"]
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0, le=1)

agent = create_agent(
    model="gpt-4.1",
    response_format=Classification,
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Classify: This is extremely important and I'm very happy!"
    }]
})
# Classification(category="urgent", sentiment="positive", confidence=0.95)
```
</ex-enum-and-literal-types>

<ex-optional-fields-and-defaults>
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class Event(BaseModel):
    title: str
    date: str
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    confirmed: bool = False
```
</ex-optional-fields-and-defaults>

<ex-union-types>
```python
from pydantic import BaseModel
from typing import Union, Literal

class EmailContact(BaseModel):
    type: Literal["email"]
    to: str
    subject: str

class PhoneContact(BaseModel):
    type: Literal["phone"]
    number: str
    message: str

ContactMethod = Union[EmailContact, PhoneContact]

agent = create_agent(
    model="gpt-4.1",
    response_format=ContactMethod,
)
# Model chooses which schema based on input
```
</ex-union-types>

<ex-array-extraction>
```python
from pydantic import BaseModel
from typing import List, Optional, Literal

class Task(BaseModel):
    title: str
    priority: Literal["high", "medium", "low"]
    due_date: Optional[str] = None

class TaskList(BaseModel):
    tasks: List[Task]

agent = create_agent(
    model="gpt-4.1",
    response_format=TaskList,
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Extract tasks: 1. Fix bug (high priority, due tomorrow) 2. Update docs"
    }]
})
```
</ex-array-extraction>

<ex-include-raw-aimessage>
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
</ex-include-raw-aimessage>

<ex-typeddict-alternative>
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
</ex-typeddict-alternative>

<ex-error-handling>
```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field, ValidationError

class StrictSchema(BaseModel):
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: int = Field(ge=0, le=120)

agent = create_agent(
    model="gpt-4.1",
    response_format=StrictSchema,
)

try:
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Email: invalid, Age: -5"}]
    })
except ValidationError as e:
    print(f"Validation failed: {e}")
```
</ex-error-handling>

<boundaries>
### What You CAN Configure

* Schema structure**: Any valid Pydantic model
* Field validation**: Types, ranges, regex, etc.
* Optional vs required**: Control field presence
* Nested objects**: Complex hierarchies
* Arrays**: Lists of items
* Enums**: Restricted values with Literal

### What You CANNOT Configure

* Model reasoning**: Can't control how model generates data
* Guarantee 100% accuracy**: Model may still make mistakes
* Force valid data if context lacks it**: Model can't invent missing info
</boundaries>

<fix-accessing-response-wrong>
```python
# WRONG: Problem: Accessing wrong key
result = agent.invoke(input)
print(result["response"])  # KeyError!

# CORRECT: Solution: Use structured_response
print(result["structured_response"])
```
</fix-accessing-response-wrong>

<fix-missing-descriptions>
```python
# WRONG: Problem: No field descriptions
class Data(BaseModel):
    date: str  # What format?
    amount: float  # What unit?

# CORRECT: Solution: Add descriptions via Field
class Data(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    amount: float = Field(description="Amount in USD")
```
</fix-missing-descriptions>

<fix-over-constraining>
```python
import re

# WRONG: Problem: Too strict for model
class Data(BaseModel):
    code: str = Field(pattern=r"^[A-Z]{2}-\d{4}-[A-Z]{3}$")  # Very specific!

# CORRECT: Solution: Use looser validation or describe format
class Data(BaseModel):
    code: str = Field(description="Format: XX-0000-XXX (letters and numbers)")
```
</fix-over-constraining>

<fix-pydantic-v1-vs-v2>
```python
# Pydantic v2 (current)
from pydantic import BaseModel, Field

class Data(BaseModel):
    value: int = Field(ge=0, le=100)

# Pydantic v1 (legacy)
from pydantic import BaseModel, Field

class Data(BaseModel):
    value: int = Field(..., ge=0, le=100)  # Note the ...

    class Config:
        # v1 config
        pass
```
</fix-pydantic-v1-vs-v2>

<fix-not-using-correct-type-hints>
```python
# WRONG: Problem: Missing type hints
class Data(BaseModel):
    items = []  # No type hint!

# CORRECT: Solution: Always use type hints
from typing import List

class Data(BaseModel):
    items: List[str] = Field(default_factory=list)
```
</fix-not-using-correct-type-hints>

<links>
- [Structured Output Overview](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Model Structured Output](https://docs.langchain.com/oss/python/langchain/models)
- [Agent Structured Output](https://docs.langchain.com/oss/python/langchain/agents)
</links>
