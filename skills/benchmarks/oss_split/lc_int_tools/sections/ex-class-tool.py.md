Create class-based tool extending BaseTool.

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DatabaseInput(BaseModel):
    customer_id: str = Field(description="Customer ID to look up")

class DatabaseQueryTool(BaseTool):
    name: str = "database_query"
    description: str = "Query the customer database for information"
    args_schema: Type[BaseModel] = DatabaseInput

    def _run(self, customer_id: str) -> str:
        """Use the tool."""
        # Your database logic
        customer = db.get_customer(customer_id)
        return str(customer)

    async def _arun(self, customer_id: str) -> str:
        """Async version."""
        # Async implementation
        raise NotImplementedError("Async not implemented")

db_tool = DatabaseQueryTool()
```
