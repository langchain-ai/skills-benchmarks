---
name: LangChain Structured Output & HITL (Python)
description: "INVOKE THIS SKILL when you need structured/typed output from LLMs OR human-in-the-loop approval. Covers with_structured_output(), Pydantic schemas, union types for multiple formats, and HITL middleware. CRITICAL: Fixes for accessing structured response wrong, missing field descriptions, and Pydantic v1 vs v2."
---

<overview>
Two critical patterns for production agents:

1. **Structured Output**: Transform unstructured model responses into validated, typed data using Pydantic schemas
2. **Human-in-the-Loop**: Add human oversight to agent tool calls, pausing for approval before sensitive actions

**Key Concepts:**
- **response_format**: Define expected output schema
- **with_structured_output()**: Model method for direct structured output
- **human_in_the_loop_middleware**: Pauses execution for human decisions
- **Interrupts**: Checkpoint where agent waits for human input
</overview>

<when-to-use-structured-output>

| Use Case | Use Structured Output? | Why |
|----------|----------------------|-----|
| Extract contact info, dates, etc. | Yes | Reliable data extraction |
| Form filling | Yes | Validate all required fields |
| API integration | Yes | Type-safe responses |
| Classification tasks | Yes | Enum validation |
| Open-ended Q&A | No | Free-form text is fine |

</when-to-use-structured-output>

---

## Structured Output

<ex-basic-structured-output>
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
</ex-basic-structured-output>

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
```
</ex-enum-and-literal-types>

<ex-complex-nested-schema>
```python
from pydantic import BaseModel, Field
from typing import List, Optional

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
```
</ex-complex-nested-schema>

---

## Human-in-the-Loop

<ex-basic-hitl-setup>
```python
from langchain.agents import create_agent, human_in_the_loop_middleware
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required for HITL
    middleware=[
        human_in_the_loop_middleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
            }
        )
    ],
)
```
</ex-basic-hitl-setup>

<ex-running-with-interrupts>
```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent runs until it needs to call tool
result1 = agent.invoke({
    "messages": [{"role": "user", "content": "Send email to john@example.com"}]
}, config=config)

# Check for interrupt
if "__interrupt__" in result1:
    interrupt = result1["__interrupt__"][0]
    print(f"Waiting for approval: {interrupt.value}")

# Step 2: Human approves
result2 = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)

# Tool now executes and agent completes
print(result2["messages"][-1].content)
```
</ex-running-with-interrupts>

<ex-editing-tool-arguments>
```python
# Human edits the arguments
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "edit",
            "args": {
                "to": "alice@company.com",  # Fixed email
                "subject": "Project Meeting - Updated",
                "body": "...",
            },
        }]
    }),
    config=config
)
```
</ex-editing-tool-arguments>

<ex-rejecting-with-feedback>
```python
# Human rejects
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "reject",
            "feedback": "Cannot delete customer data without manager approval",
        }]
    }),
    config=config
)
```
</ex-rejecting-with-feedback>

<ex-multiple-tools-different-policies>
```python
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email, read_email, delete_email],
    checkpointer=MemorySaver(),
    middleware=[
        human_in_the_loop_middleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "delete_email": {"allowed_decisions": ["approve", "reject"]},  # No edit
                "read_email": False,  # No HITL for reading
            }
        )
    ],
)
```
</ex-multiple-tools-different-policies>

<boundaries>
### What You CAN Configure

**Structured Output:**
- Schema structure: Any valid Pydantic model
- Field validation: Types, ranges, regex, etc.
- Nested objects, arrays, enums

**HITL:**
- Which tools require approval
- Allowed decisions per tool (approve, edit, reject)
- Checkpointer for persistence

### What You CANNOT Configure

- Model reasoning: Can't control how model generates data
- Guarantee 100% accuracy: Model may still make mistakes
- Skip checkpointer requirement for HITL
</boundaries>

<fix-accessing-response-wrong>
```python
# WRONG: Accessing wrong key
result = agent.invoke(input)
print(result["response"])  # KeyError!

# CORRECT: Use structured_response
print(result["structured_response"])
```
</fix-accessing-response-wrong>

<fix-missing-descriptions>
```python
# WRONG: No field descriptions - model guesses format
class Data(BaseModel):
    date: str  # What format?
    amount: float  # What unit?

# CORRECT: Add descriptions via Field
class Data(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    amount: float = Field(description="Amount in USD")
```
</fix-missing-descriptions>

<fix-not-using-correct-type-hints>
```python
# WRONG: Missing type hints
class Data(BaseModel):
    items = []  # No type hint!

# CORRECT: Always use type hints
from typing import List

class Data(BaseModel):
    items: List[str] = Field(default_factory=list)
```
</fix-not-using-correct-type-hints>

<fix-missing-checkpointer>
```python
# WRONG: No checkpointer for HITL
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    middleware=[human_in_the_loop_middleware({...})],  # Error!
)

# CORRECT: Always add checkpointer
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required
    middleware=[human_in_the_loop_middleware({...})],
)
```
</fix-missing-checkpointer>

<fix-no-thread-id>
```python
# WRONG: Missing thread_id
agent.invoke(input)  # No config!

# CORRECT: Always provide thread_id
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
</fix-no-thread-id>

<fix-wrong-resume-syntax>
```python
# WRONG: Wrong resume format
agent.invoke({"resume": {"decisions": [...]}})  # Wrong!

# CORRECT: Use Command
from langgraph.types import Command

agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
```
</fix-wrong-resume-syntax>
