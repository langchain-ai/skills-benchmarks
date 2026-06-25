Factory function creating tools:

```python
from langchain.tools import tool
import os

def create_database_tool(connection_string: str):
    """Factory function to create database tool with specific config."""

    @tool
    def query_database(query: str) -> str:
        """Execute SQL query on the database.

        Args:
            query: SQL query to execute
        """
        results = db.query(query)  # Uses connection_string from closure
        return json.dumps(results)

    return query_database

prod_db_tool = create_database_tool(os.getenv("PROD_DB_URL"))
dev_db_tool = create_database_tool(os.getenv("DEV_DB_URL"))
```
