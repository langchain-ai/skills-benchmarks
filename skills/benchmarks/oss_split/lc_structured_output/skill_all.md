---
name: LangChain Structured Output
description: "[LangChain] Get structured, validated output from LangChain agents and models using Pydantic/Zod schemas, type-safe responses, and automatic validation"
---

<oneliner>
Get structured, validated output from LangChain agents and models using Pydantic/Zod schemas, type-safe responses, and automatic validation.
</oneliner>

<overview>
Structured output transforms unstructured model responses into validated, typed data. Instead of parsing free text, you get Python objects or JSON conforming to your schema - perfect for extracting data, building forms, or integrating with downstream systems.

Key Concepts:
- **response_format / responseFormat**: Define expected output schema
- **Pydantic Validation (Python)**: Type-safe schemas with automatic validation
- **Zod Validation (TypeScript)**: Type-safe schemas with automatic validation
- **with_structured_output() / withStructuredOutput()**: Model method for direct structured output
- **Tool Strategy**: Uses tool calling under the hood for models without native support
</overview>

<when-to-use>

| Use Case | Use Structured Output? | Why |
|----------|----------------------|-----|
| Extract contact info, dates, etc. | Yes | Reliable data extraction |
| Form filling | Yes | Validate all required fields |
| API integration | Yes | Type-safe responses |
| Classification tasks | Yes | Enum validation |
| Open-ended Q&A | No | Free-form text is fine |
| Creative writing | No | Don't constrain creativity |

</when-to-use>

<schema-options>

| Schema Type | Language | When to Use | Example |
|-------------|----------|-------------|---------|
| Pydantic model | Python | Python projects (recommended) | `class Model(BaseModel):` |
| Zod schema | TypeScript | TypeScript projects (recommended) | `z.object({...})` |
| TypedDict | Python | Simpler typing | `class Data(TypedDict):` |
| JSON Schema | Both | Interoperability | `{"type": "object", ...}` |
| Union types | Both | Multiple possible formats | `Union[Schema1, Schema2]` / `z.union([...])` |

</schema-options>

<ex-basic-agent>
<python>
Extract contact info with Pydantic validation.

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
</python>

<typescript>
Extract contact info with Zod validation.

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string(),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactInfo,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract: John Doe, john@example.com, (555) 123-4567"
  }],
});

console.log(result.structuredResponse);
// { name: 'John Doe', email: 'john@example.com', phone: '(555) 123-4567' }
```
</typescript>
</ex-basic-agent>

<ex-model-direct>
<python>
Use with_structured_output on model directly.

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
</python>

<typescript>
Use withStructuredOutput on model directly.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const MovieSchema = z.object({
  title: z.string().describe("Movie title"),
  year: z.number().describe("Release year"),
  director: z.string(),
  rating: z.number().min(0).max(10),
});

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(MovieSchema);

const response = await structuredModel.invoke("Tell me about Inception");
console.log(response);
// { title: "Inception", year: 2010, director: "Christopher Nolan", rating: 8.8 }
```
</typescript>
</ex-model-direct>

<ex-nested-schema>
<python>
Define nested Pydantic models for complex data.

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
</python>

<typescript>
Define nested Zod schemas for complex data.

```typescript
import { z } from "zod";

const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string(),
  zip: z.string(),
});

const PersonSchema = z.object({
  name: z.string(),
  age: z.number().int().positive(),
  email: z.string().email(),
  address: AddressSchema,
  tags: z.array(z.string()),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: PersonSchema,
});
```
</typescript>
</ex-nested-schema>

<ex-enum-literal>
<python>
Classify with Literal types for enums.

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
</python>

<typescript>
Classify with z.enum for restricted values.

```typescript
import { z } from "zod";

const ClassificationSchema = z.object({
  category: z.enum(["urgent", "normal", "low"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  confidence: z.number().min(0).max(1),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ClassificationSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Classify: This is extremely important and I'm very happy!"
  }],
});
// { category: "urgent", sentiment: "positive", confidence: 0.95 }
```
</typescript>
</ex-enum-literal>

<ex-optional-defaults>
<python>
Optional fields and default values.

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
</python>

<typescript>
Optional fields and default values.

```typescript
import { z } from "zod";

const EventSchema = z.object({
  title: z.string(),
  date: z.string(),
  location: z.string().optional(),
  attendees: z.array(z.string()).default([]),
  confirmed: z.boolean().default(false),
});
```
</typescript>
</ex-optional-defaults>

<ex-union-types>
<python>
Union types for multiple possible schemas.

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
</python>

<typescript>
Union types for multiple possible schemas.

```typescript
import { z } from "zod";

const EmailSchema = z.object({
  type: z.literal("email"),
  to: z.string().email(),
  subject: z.string(),
});

const PhoneSchema = z.object({
  type: z.literal("phone"),
  number: z.string(),
  message: z.string(),
});

const ContactSchema = z.union([EmailSchema, PhoneSchema]);

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactSchema,
});
// Model chooses which schema based on input
```
</typescript>
</ex-union-types>

<ex-array-extraction>
<python>
Extract lists of items from text.

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
</python>

<typescript>
Extract lists of items from text.

```typescript
import { z } from "zod";

const TaskListSchema = z.object({
  tasks: z.array(z.object({
    title: z.string(),
    priority: z.enum(["high", "medium", "low"]),
    dueDate: z.string().optional(),
  })),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: TaskListSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract tasks: 1. Fix bug (high priority, due tomorrow) 2. Update docs"
  }],
});
```
</typescript>
</ex-array-extraction>

<ex-include-raw>
<python>
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
</python>

<typescript>
Get both raw message and parsed output.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const schema = z.object({ name: z.string(), age: z.number() });

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(schema, {
  includeRaw: true,
});

const response = await structuredModel.invoke("Person: Alice, 30 years old");
console.log(response);
// {
//   raw: AIMessage { ... },
//   parsed: { name: "Alice", age: 30 }
// }
```
</typescript>
</ex-include-raw>

<ex-typeddict>
<python>
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
</python>
</ex-typeddict>

<ex-error-handling>
<python>
Handle validation errors with try/except.

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
</python>

<typescript>
Handle validation errors with try/catch.

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const StrictSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(120),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: StrictSchema,
});

try {
  const result = await agent.invoke({
    messages: [{ role: "user", content: "Email: invalid, Age: -5" }],
  });
} catch (error) {
  console.error("Validation failed:", error);
  // Model will retry or return error
}
```
</typescript>
</ex-error-handling>

<boundaries>
What You CAN Configure:
- **Schema structure**: Any valid Pydantic model or Zod schema
- **Field validation**: Types, ranges, regex, etc.
- **Optional vs required**: Control field presence
- **Nested objects**: Complex hierarchies
- **Arrays**: Lists of items
- **Enums**: Restricted values with Literal/z.enum

What You CANNOT Configure:
- **Model reasoning**: Can't control how model generates data
- **Guarantee 100% accuracy**: Model may still make mistakes
- **Force valid data if context lacks it**: Model can't invent missing info
</boundaries>

<fix-accessing-response-wrong>
<python>
Access structured_response, not response.

```python
# Problem: Accessing wrong key
result = agent.invoke(input)
print(result["response"])  # KeyError!

# Solution: Use structured_response
print(result["structured_response"])
```
</python>

<typescript>
Access structuredResponse, not response.

```typescript
// Problem: Accessing wrong property
const result = await agent.invoke(input);
console.log(result.response);  // undefined!

// Solution: Use structuredResponse
console.log(result.structuredResponse);
```
</typescript>
</fix-accessing-response-wrong>

<fix-missing-descriptions>
<python>
Add Field descriptions for clarity.

```python
# Problem: No field descriptions
class Data(BaseModel):
    date: str  # What format?
    amount: float  # What unit?

# Solution: Add descriptions via Field
class Data(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    amount: float = Field(description="Amount in USD")
```
</python>

<typescript>
Add describe() calls for clarity.

```typescript
// Problem: No field descriptions
const schema = z.object({
  date: z.string(),  // What format?
  amount: z.number(),  // What unit?
});

// Solution: Add descriptions
const schema = z.object({
  date: z.string().describe("Date in YYYY-MM-DD format"),
  amount: z.number().describe("Amount in USD"),
});
```
</typescript>
</fix-missing-descriptions>

<fix-over-constraining>
<python>
Avoid overly strict regex patterns.

```python
import re

# Problem: Too strict for model
class Data(BaseModel):
    code: str = Field(pattern=r"^[A-Z]{2}-\d{4}-[A-Z]{3}$")  # Very specific!

# Solution: Use looser validation or describe format
class Data(BaseModel):
    code: str = Field(description="Format: XX-0000-XXX (letters and numbers)")
```
</python>

<typescript>
Avoid overly strict regex patterns.

```typescript
// Problem: Too strict for model
const schema = z.object({
  code: z.string().regex(/^[A-Z]{2}-\d{4}-[A-Z]{3}$/),  // Very specific!
});

// Solution: Validate post-processing or use looser schema
const schema = z.object({
  code: z.string().describe("Format: XX-0000-XXX (letters and numbers)"),
});
```
</typescript>
</fix-over-constraining>

<fix-pydantic-v1-v2>
<python>
Pydantic v2 vs v1 syntax differences.

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
</python>
</fix-pydantic-v1-v2>

<fix-type-hints>
<python>
Always use type hints for fields.

```python
# Problem: Missing type hints
class Data(BaseModel):
    items = []  # No type hint!

# Solution: Always use type hints
from typing import List

class Data(BaseModel):
    items: List[str] = Field(default_factory=list)
```
</python>
</fix-type-hints>

<fix-validation-errors>
<typescript>
Always wrap invoke in try/catch.

```typescript
// Problem: No error handling
const result = await agent.invoke(input);
const data = result.structuredResponse;  // May throw!

// Solution: Try/catch or check for errors
try {
  const result = await agent.invoke(input);
  const data = result.structuredResponse;
} catch (error) {
  console.error("Failed to get structured output:", error);
}
```
</typescript>
</fix-validation-errors>

<fix-responseformat-tools>
<typescript>
responseFormat extracts from final response only.

```typescript
// Problem: Using responseFormat with tools incorrectly
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  responseFormat: MySchema,  // Will extract from FINAL response only
});
// Tools run first, then schema extracted from final response

// This is correct if you want tools + structured final output
// Just understand the flow
```
</typescript>
</fix-responseformat-tools>

<documentation-links>
Python:
- [Structured Output Overview](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Model Structured Output](https://docs.langchain.com/oss/python/langchain/models)
- [Agent Structured Output](https://docs.langchain.com/oss/python/langchain/agents)

TypeScript:
- [Structured Output Overview](https://docs.langchain.com/oss/javascript/langchain/structured-output)
- [Model Structured Output](https://docs.langchain.com/oss/javascript/langchain/models)
- [Agent Structured Output](https://docs.langchain.com/oss/javascript/langchain/agents)
</documentation-links>
