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
