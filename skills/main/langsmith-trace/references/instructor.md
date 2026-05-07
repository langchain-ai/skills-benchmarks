# Tracing Instructor applications

Instructor patches an OpenAI client. Wrap with LangSmith **first**, then patch with Instructor.

## Install

```bash
pip install -U langsmith instructor openai
```

## Env

```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_WORKSPACE_ID=<workspace>  # only if API key spans multiple workspaces
```

## Setup

```python
import instructor
from openai import OpenAI
from langsmith import wrappers, traceable
from pydantic import BaseModel

# Order matters: wrap with LangSmith first, then patch with Instructor.
client = wrappers.wrap_openai(OpenAI())
client = instructor.patch(client)

class UserDetail(BaseModel):
    name: str
    age: int

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=UserDetail,
    messages=[{"role": "user", "content": "Extract: Jason is 25"}],
)
```

## Nested traces

Wrap callers with `@traceable` to get a parent span around Instructor calls:

```python
@traceable(name="Extract User Details")
def my_function(text: str) -> UserDetail:
    return client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=UserDetail,
        messages=[{"role": "user", "content": f"Extract {text}"}],
    )
```

## Gotcha

Patching order is the only common bug. If you call `instructor.patch(OpenAI())` and *then* `wrap_openai(...)`, the wrapping wins but Instructor's response_model handling can break. Always wrap first.
