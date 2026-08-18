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
