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
