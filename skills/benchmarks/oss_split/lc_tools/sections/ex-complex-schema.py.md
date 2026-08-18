Tool with Pydantic schema:

```python
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, Literal

class SearchFilters(BaseModel):
    status: Optional[Literal["active", "inactive", "pending"]] = None
    created_after: Optional[str] = Field(None, description="ISO date string")

class SearchParams(BaseModel):
    query: str = Field(description="Search query (keywords or customer name)")
    limit: int = Field(default=10, description="Maximum number of results")
    filters: Optional[SearchFilters] = None

@tool(args_schema=SearchParams)
def search_database(query: str, limit: int = 10, filters: Optional[dict] = None) -> str:
    """Search the customer database for records matching criteria."""
    return f"Found {limit} results for: {query}"
```
