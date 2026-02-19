---
name: LangChain Tools (Python)
description: "[LangChain] Define and use tools in LangChain - includes @tool decorator, custom tools, built-in tools, and tool schemas"
---

<overview>
Tools are functions that agents can execute to perform actions like fetching data, running code, or querying databases. Tools have schemas that describe their purpose and parameters, helping models understand when and how to use them.

**Key Concepts:**
- **@tool**: Decorator to create tools from functions
- **Schema**: Pydantic models or type hints defining parameters
- **Description**: Helps model understand when to use the tool
- **Built-in Tools**: Pre-made tools for common tasks
</overview>

<when-to-define-custom-tools>

| Scenario | Create Custom Tool? | Why |
|----------|---------------------|-----|
| Domain-specific logic | Yes | Unique to your application |
| Third-party API integration | Yes | Custom integration needed |
| Database queries | Yes | Your schema/data |
| Common utilities (search, calc) | Partial Maybe | Check for existing tools first |
| File operations | Partial Maybe | Built-in filesystem tools exist |

</when-to-define-custom-tools>

<tool-definition-methods>

| Method | When to Use | Example |
|--------|-------------|---------|
| `@tool` decorator | Simple functions | Basic transformations |
| `@tool` with Pydantic | Complex parameters | Multiple typed fields |
| `StructuredTool` | Full control | Custom error handling |
| Built-in tools | Common operations | Search, code execution |

</tool-definition-methods>

<ex-basic-tool-definition>
```python
from langchain.tools import tool
from typing import Literal

@tool
def calculator(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> float:
    """Perform mathematical calculations.

    Use this when you need to compute numbers.

    Args:
        operation: The mathematical operation to perform
        a: First number
        b: Second number
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Use with agent
result = calculator.invoke({
    "operation": "add",
    "a": 5,
    "b": 3,
})
print(result)  # "8.0"
```
</ex-basic-tool-definition>

<ex-tool-with-pydantic-schema>
```python
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

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
    # Your database search logic
    return f"Found {limit} results for: {query}"
```
</ex-tool-with-pydantic-schema>

<ex-async-tool>
```python
from langchain.tools import tool
import aiohttp

@tool
async def fetch_weather(location: str) -> str:
    """Get current weather conditions for a location.

    Args:
        location: City name or ZIP code
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.weather.com/v1/location/{location}"
        ) as response:
            data = await response.json()
            return f"Temperature: {data['temp']}F, Conditions: {data['conditions']}"
```
</ex-async-tool>

<ex-tool-with-error-handling>
```python
from langchain.tools import tool

@tool
def divide(numerator: float, denominator: float) -> float:
    """Divide two numbers.

    Args:
        numerator: The number to divide
        denominator: The number to divide by
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

# Error will be caught and returned as ToolMessage
```
</ex-tool-with-error-handling>

<ex-tool-with-side-effects>
```python
from langchain.tools import tool
from pathlib import Path

@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.

    Use carefully as this modifies the filesystem.

    Args:
        filepath: Path to the file
        content: Content to write
    """
    Path(filepath).write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to {filepath}"
```
</ex-tool-with-side-effects>

<ex-tool-with-external-dependencies>
```python
from langchain.tools import tool
import requests
import os

@tool
def search_github(query: str, language: str = None) -> str:
    """Search GitHub repositories.

    Args:
        query: Search query
        language: Programming language filter (optional)
    """
    params = {"q": f"{query} language:{language}" if language else query, "sort": "stars"}
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}

    response = requests.get(
        "https://api.github.com/search/repositories",
        params=params,
        headers=headers,
    )

    repos = response.json()["items"][:5]
    return "\n".join([f"{r['full_name']} (stars: {r['stargazers_count']})" for r in repos])
```
</ex-tool-with-external-dependencies>

<ex-tool-with-complex-return>
```python
from langchain.tools import tool
import json

@tool
def analyze_text(text: str) -> str:
    """Analyze text statistics.

    Args:
        text: Text to analyze
    """
    words = text.split()

    stats = {
        "word_count": len(words),
        "char_count": len(text),
        "sentences": len(text.split(".")),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
    }

    return json.dumps(stats)
```
</ex-tool-with-complex-return>

<ex-tool-with-runtime-configuration>
```python
from langchain.tools import tool
from typing import Callable

def create_database_tool(connection_string: str):
    """Factory function to create database tool with specific config."""

    @tool
    def query_database(query: str) -> str:
        """Execute SQL query on the database.

        Args:
            query: SQL query to execute
        """
        # Use connection_string to connect to DB
        results = db.query(query)
        return json.dumps(results)

    return query_database

# Create tools with specific configurations
prod_db_tool = create_database_tool(os.getenv("PROD_DB_URL"))
dev_db_tool = create_database_tool(os.getenv("DEV_DB_URL"))
```
</ex-tool-with-runtime-configuration>

<ex-multiple-related-tools>
```python
from langchain.tools import tool

# Toolkit pattern: group of related tools
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email message.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    # Send email logic
    return f"Email sent to {to}"

@tool
def read_emails(folder: str = "inbox", limit: int = 10) -> str:
    """Read emails from a folder.

    Args:
        folder: Email folder name (default: inbox)
        limit: Maximum emails to retrieve (default: 10)
    """
    # Read emails logic
    return f"Retrieved {limit} emails from {folder}"

# Group related tools
email_tools = [send_email, read_emails]

# Use all email tools
from langchain.agents import create_agent
agent = create_agent(
    model="gpt-4.1",
    tools=email_tools,
)
```
</ex-multiple-related-tools>

<ex-tool-with-pydantic-field-descriptions>
```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class UserLookup(BaseModel):
    user_id: str = Field(description="User ID to lookup")

@tool(args_schema=UserLookup)
def get_user(user_id: str) -> str:
    """Get user information by ID."""
    user = db.users.find_by_id(user_id)

    return json.dumps({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created": user.created_at.isoformat(),
    })
```
</ex-tool-with-pydantic-field-descriptions>

<ex-tool-with-streaming-updates>
```python
from langchain.tools import tool

@tool
async def process_large_file(filepath: str, runtime) -> str:
    """Process a large file with progress updates.

    Args:
        filepath: Path to file to process
    """
    total_lines = 1000

    for i in range(0, total_lines, 100):
        # Stream progress updates
        await runtime.stream_writer.write({
            "type": "progress",
            "data": {"processed": i, "total": total_lines},
        })

        # Process chunk
        await process_chunk(i, i + 100)

    return "Processing complete"
```
</ex-tool-with-streaming-updates>

<ex-structured-tool>
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    operation: str = Field(description="Operation to perform")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")

def _calculate(operation: str, a: float, b: float) -> float:
    """Internal calculation logic."""
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y,
    }
    return operations[operation](a, b)

calculator_tool = StructuredTool.from_function(
    func=_calculate,
    name="calculator",
    description="Perform mathematical calculations",
    args_schema=CalculatorInput,
)
```
</ex-structured-tool>

<boundaries>
### What You CAN Configure

* Function logic**: Any Python code
* Parameters**: Via type hints or Pydantic models
* Name and description**: Guide model's tool selection
* Return value**: Any serializable data (string, JSON, etc.)
* Async operations**: Tools can be async
* Error handling**: Raise exceptions or return error messages

### What You CANNOT Configure

* When model calls tool**: Model decides based on context
* Tool call order**: Model determines execution flow
* Parameter values**: Model generates based on schema
* Response format from model**: Tool returns, model interprets
</boundaries>

<fix-poor-tool-descriptions>
```python
# WRONG: Problem: Vague description
@tool
def bad_tool(data: str) -> str:
    """Does something with data."""  # Too vague!
    return "result"

# CORRECT: Solution: Specific, actionable description
@tool
def search_customers(query: str) -> str:
    """Search customer database by name, email, or ID.

    Returns customer records with contact information.
    Use this when user asks about customer data.

    Args:
        query: Customer name, email, or ID to search for
    """
    return search_database(query)
```
</fix-poor-tool-descriptions>

<fix-missing-type-hints>
```python
# WRONG: Problem: No type hints
@tool
def bad_tool(query, limit):  # No types!
    """Search database."""
    return "result"

# CORRECT: Solution: Always use type hints
@tool
def good_tool(query: str, limit: int = 10) -> str:
    """Search database.

    Args:
        query: Search terms or keywords
        limit: Maximum results to return (1-100)
    """
    return "result"
```
</fix-missing-type-hints>

<fix-non-serializable-return>
```python
from datetime import datetime

# WRONG: Problem: Returning complex objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime not JSON-serializable

# CORRECT: Solution: Return strings or JSON
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()

# Or stringify objects
import json

@tool
def get_data() -> str:
    """Get data."""
    return json.dumps({
        "timestamp": datetime.now().timestamp(),
        "user": get_current_user(),
    })
```
</fix-non-serializable-return>

<fix-missing-docstrings>
```python
# WRONG: Problem: No docstring
@tool
def bad_tool(input: str) -> str:
    return "result"  # No description!

# CORRECT: Solution: Always provide docstring
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Use this tool when you need to transform user input.

    Args:
        input: The data to process
    """
    return "result"
```
</fix-missing-docstrings>

<fix-forgetting-async>
```python
import requests

# WRONG: Problem: Using sync in async context
@tool
async def bad_fetch(url: str) -> str:
    """Fetch URL."""
    response = requests.get(url)  # Blocking!
    return response.text

# CORRECT: Solution: Use async libraries
import aiohttp

@tool
async def good_fetch(url: str) -> str:
    """Fetch URL content.

    Args:
        url: URL to fetch
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```
</fix-forgetting-async>

<fix-tool-names-with-special-chars>
```python
# WRONG: Problem: Invalid tool name
@tool(name="Get Weather!")  # Special chars not allowed
def bad_tool() -> str:
    """Get weather."""
    return "result"

# CORRECT: Solution: Use snake_case
@tool(name="get_weather")  # Valid name
def good_tool() -> str:
    """Get weather."""
    return "result"

# Or let decorator infer from function name
@tool
def get_weather() -> str:  # Name will be "get_weather"
    """Get weather."""
    return "result"
```
</fix-tool-names-with-special-chars>

<links>
- [Tools Overview](https://docs.langchain.com/oss/python/langchain/tools)
- [Tool Integrations](https://docs.langchain.com/oss/python/integrations/tools/index)
- [Custom Tools Guide](https://docs.langchain.com/oss/python/integrations/chat/openai)
</links>
