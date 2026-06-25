Define a tool with explicit Pydantic schema for argument validation.
```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Max results")

@tool(args_schema=SearchParams)
def search_database(query: str, limit: int = 10) -> str:
    """Search the database for records."""
    return f"Found {limit} results for: {query}"
```
