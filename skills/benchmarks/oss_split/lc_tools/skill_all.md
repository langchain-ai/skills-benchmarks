---
name: LangChain Tools
description: "[LangChain] Define and use tools in LangChain - includes @tool decorator, custom tools, built-in tools, and tool schemas"
---

## Overview

Tools are functions that agents can execute to perform actions like fetching data, running code, or querying databases. Tools have schemas that describe their purpose and parameters, helping models understand when and how to use them.

**Key Concepts:**
- **@tool / tool()**: Decorator/function to create tools
- **Schema**: Pydantic models (Python) or Zod schemas (TypeScript) defining parameters
- **Description**: Helps model understand when to use the tool
- **Built-in Tools**: Pre-made tools for common tasks

## When to Define Custom Tools

| Scenario | Create Custom Tool? | Why |
|----------|---------------------|-----|
| Domain-specific logic | Yes | Unique to your application |
| Third-party API integration | Yes | Custom integration needed |
| Database queries | Yes | Your schema/data |
| Common utilities (search, calc) | Maybe | Check for existing tools first |
| File operations | Maybe | Built-in filesystem tools exist |

## Tool Definition Methods

| Method | When to Use | Example |
|--------|-------------|---------|
| `@tool` / `tool()` | Simple functions | Basic transformations |
| Schema-based | Complex parameters | Multiple typed fields |
| `StructuredTool` | Full control | Custom error handling |
| Built-in tools | Common operations | Search, code execution |

## Code Examples

### Basic Tool Definition

#### Python

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

result = calculator.invoke({"operation": "add", "a": 5, "b": 3})
print(result)  # "8.0"
```

#### TypeScript

```typescript
import { tool } from "langchain";
import { z } from "zod";

const calculator = tool(
  async ({ operation, a, b }: { operation: string; a: number; b: number }) => {
    if (operation === "add") return a + b;
    if (operation === "subtract") return a - b;
    if (operation === "multiply") return a * b;
    if (operation === "divide") return a / b;
    throw new Error(`Unknown operation: ${operation}`);
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations. Use this when you need to compute numbers.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]).describe("The mathematical operation"),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);

const result = await calculator.invoke({ operation: "add", a: 5, b: 3 });
console.log(result); // "8"
```

### Tool with Complex Schema

#### Python

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

#### TypeScript

```typescript
const searchDatabase = tool(
  async ({ query, limit, filters }) => {
    return `Found ${limit} results for: ${query}`;
  },
  {
    name: "search_database",
    description: "Search the customer database for records matching criteria",
    schema: z.object({
      query: z.string().describe("Search query (keywords or customer name)"),
      limit: z.number().default(10).describe("Maximum number of results to return"),
      filters: z.object({
        status: z.enum(["active", "inactive", "pending"]).optional(),
        created_after: z.string().optional().describe("ISO date string"),
      }).optional(),
    }),
  }
);
```

### Async Tool

#### Python

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
        async with session.get(f"https://api.weather.com/v1/location/{location}") as response:
            data = await response.json()
            return f"Temperature: {data['temp']}°F, Conditions: {data['conditions']}"
```

#### TypeScript

```typescript
const fetchWeather = tool(
  async ({ location }: { location: string }) => {
    const response = await fetch(`https://api.weather.com/v1/location/${location}`);
    const data = await response.json();
    return `Temperature: ${data.temp}°F, Conditions: ${data.conditions}`;
  },
  {
    name: "get_weather",
    description: "Get current weather conditions for a location",
    schema: z.object({
      location: z.string().describe("City name or ZIP code"),
    }),
  }
);
```

### Tool with Error Handling

#### Python

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

#### TypeScript

```typescript
const divisionTool = tool(
  async ({ numerator, denominator }) => {
    if (denominator === 0) {
      throw new Error("Cannot divide by zero");
    }
    return numerator / denominator;
  },
  {
    name: "divide",
    description: "Divide two numbers",
    schema: z.object({
      numerator: z.number(),
      denominator: z.number(),
    }),
  }
);
```

### Tool with Side Effects

#### Python

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

#### TypeScript

```typescript
import fs from "fs/promises";

const writeFile = tool(
  async ({ filepath, content }) => {
    await fs.writeFile(filepath, content, "utf-8");
    return `Successfully wrote ${content.length} characters to ${filepath}`;
  },
  {
    name: "write_file",
    description: "Write content to a file. Use carefully as this modifies the filesystem.",
    schema: z.object({
      filepath: z.string().describe("Path to the file"),
      content: z.string().describe("Content to write"),
    }),
  }
);
```

### Tool with External Dependencies

#### Python

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

#### TypeScript

```typescript
import axios from "axios";

const githubSearch = tool(
  async ({ query, language }) => {
    const response = await axios.get("https://api.github.com/search/repositories", {
      params: { q: `${query} language:${language}`, sort: "stars" },
      headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
    });

    const repos = response.data.items.slice(0, 5);
    return repos.map(r => `${r.full_name} (stars: ${r.stargazers_count})`).join("\n");
  },
  {
    name: "search_github",
    description: "Search GitHub repositories",
    schema: z.object({
      query: z.string().describe("Search query"),
      language: z.string().optional().describe("Programming language filter"),
    }),
  }
);
```

### Tool with Complex Return Type

#### Python

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

#### TypeScript

```typescript
const analyzeText = tool(
  async ({ text }) => {
    const words = text.split(/\s+/);
    return JSON.stringify({
      word_count: words.length,
      char_count: text.length,
      sentences: text.split(/[.!?]+/).length,
      avg_word_length: words.reduce((sum, w) => sum + w.length, 0) / words.length,
    });
  },
  {
    name: "analyze_text",
    description: "Analyze text statistics",
    schema: z.object({
      text: z.string().describe("Text to analyze"),
    }),
  }
);
```

### Tool with Runtime Configuration (Factory Pattern)

#### Python

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

#### TypeScript

```typescript
function createDatabaseTool(connectionString: string) {
  return tool(
    async ({ query }) => {
      const results = await db.query(query);  // Uses connectionString from closure
      return JSON.stringify(results);
    },
    {
      name: "query_database",
      description: "Execute SQL query on the database",
      schema: z.object({
        query: z.string().describe("SQL query to execute"),
      }),
    }
  );
}

const prodDbTool = createDatabaseTool(process.env.PROD_DB_URL);
const devDbTool = createDatabaseTool(process.env.DEV_DB_URL);
```

### Multiple Related Tools (Toolkit Pattern)

#### Python

```python
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email message.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    return f"Email sent to {to}"

@tool
def read_emails(folder: str = "inbox", limit: int = 10) -> str:
    """Read emails from a folder.

    Args:
        folder: Email folder name (default: inbox)
        limit: Maximum emails to retrieve (default: 10)
    """
    return f"Retrieved {limit} emails from {folder}"

email_tools = [send_email, read_emails]

from langchain.agents import create_agent
agent = create_agent(model="gpt-4.1", tools=email_tools)
```

#### TypeScript

```typescript
const emailTools = {
  send: tool(
    async ({ to, subject, body }) => `Email sent to ${to}`,
    {
      name: "send_email",
      description: "Send an email message",
      schema: z.object({
        to: z.string().email(),
        subject: z.string(),
        body: z.string(),
      }),
    }
  ),

  read: tool(
    async ({ folder, limit }) => `Retrieved ${limit} emails from ${folder}`,
    {
      name: "read_emails",
      description: "Read emails from a folder",
      schema: z.object({
        folder: z.string().default("inbox"),
        limit: z.number().default(10),
      }),
    }
  ),
};

const agent = createAgent({
  model: "gpt-4.1",
  tools: Object.values(emailTools),
});
```

### Tool with Streaming Updates

#### Python

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
        await runtime.stream_writer.write({
            "type": "progress",
            "data": {"processed": i, "total": total_lines},
        })
        await process_chunk(i, i + 100)

    return "Processing complete"
```

#### TypeScript

```typescript
const processLargeFile = tool(
  async ({ filepath }, { runtime }) => {
    const totalLines = 1000;

    for (let i = 0; i < totalLines; i += 100) {
      await runtime.stream_writer.write({
        type: "progress",
        data: { processed: i, total: totalLines },
      });
      await processChunk(i, i + 100);
    }

    return "Processing complete";
  },
  {
    name: "process_file",
    description: "Process a large file with progress updates",
    schema: z.object({ filepath: z.string() }),
  }
);
```

### Tool with StructuredTool (Python)

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

## Boundaries

### What You CAN Configure

- **Function logic**: Any Python/TypeScript code
- **Parameters**: Via type hints/Pydantic (Python) or Zod schemas (TypeScript)
- **Name and description**: Guide model's tool selection
- **Return value**: Any serializable data (string, JSON, etc.)
- **Async operations**: Tools can be async
- **Error handling**: Raise exceptions or return error messages

### What You CANNOT Configure

- **When model calls tool**: Model decides based on context
- **Tool call order**: Model determines execution flow
- **Parameter values**: Model generates based on schema
- **Response format from model**: Tool returns, model interprets

## Gotchas

### 1. Poor Tool Descriptions

#### Python

```python
# BAD: Vague description
@tool
def bad_tool(data: str) -> str:
    """Does something with data."""  # Too vague!
    return "result"

# GOOD: Specific, actionable description
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

#### TypeScript

```typescript
// BAD: Vague description
const badTool = tool(
  async ({ data }) => "result",
  { name: "tool", description: "Does something with data", schema: z.object({ data: z.string() }) }
);

// GOOD: Specific, actionable description
const goodTool = tool(
  async ({ query }) => searchDatabase(query),
  {
    name: "search_customers",
    description: "Search customer database by name, email, or ID. Returns customer records with contact info.",
    schema: z.object({ query: z.string().describe("Customer name, email, or ID") }),
  }
);
```

### 2. Missing Type Hints / Schema Descriptions

#### Python

```python
# BAD: No type hints
@tool
def bad_tool(query, limit):  # No types!
    """Search database."""
    return "result"

# GOOD: Always use type hints
@tool
def good_tool(query: str, limit: int = 10) -> str:
    """Search database.

    Args:
        query: Search terms or keywords
        limit: Maximum results to return (1-100)
    """
    return "result"
```

#### TypeScript

```typescript
// BAD: No field descriptions
const badSchema = z.object({ query: z.string(), limit: z.number() });

// GOOD: Describe each field
const goodSchema = z.object({
  query: z.string().describe("Search terms or keywords"),
  limit: z.number().describe("Maximum results to return (1-100)"),
});
```

### 3. Non-Serializable Return Values

#### Python

```python
from datetime import datetime

# BAD: Returning complex objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime not JSON-serializable

# GOOD: Return strings or JSON
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()
```

#### TypeScript

```typescript
// BAD: Returning complex objects
const badTool = tool(async () => new Date(), { name: "get_time", description: "Get time", schema: z.object({}) });

// GOOD: Return strings or JSON
const goodTool = tool(async () => new Date().toISOString(), { name: "get_time", description: "Get time", schema: z.object({}) });
```

### 4. Missing Docstrings (Python)

```python
# BAD: No docstring
@tool
def bad_tool(input: str) -> str:
    return "result"  # No description!

# GOOD: Always provide docstring
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Use this tool when you need to transform user input.

    Args:
        input: The data to process
    """
    return "result"
```

### 5. Forgetting Async / Not Awaiting

#### Python

```python
import requests
import aiohttp

# BAD: Using sync in async context
@tool
async def bad_fetch(url: str) -> str:
    """Fetch URL."""
    response = requests.get(url)  # Blocking!
    return response.text

# GOOD: Use async libraries
@tool
async def good_fetch(url: str) -> str:
    """Fetch URL content."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

#### TypeScript

```typescript
// BAD: Not awaiting async operations
const badTool = tool(
  ({ url }) => { fetch(url); return "done"; },  // Not awaited!
  { name: "fetch_url", description: "Fetch URL", schema: z.object({ url: z.string() }) }
);

// GOOD: Use async/await
const goodTool = tool(
  async ({ url }) => {
    const response = await fetch(url);
    return await response.text();
  },
  { name: "fetch_url", description: "Fetch URL content", schema: z.object({ url: z.string().url() }) }
);
```

### 6. Tool Names with Spaces or Special Characters

```python
# BAD: Invalid tool name
@tool(name="Get Weather!")  # Special chars not allowed
def bad_tool() -> str:
    return "result"

# GOOD: Use snake_case
@tool(name="get_weather")  # Valid name
def good_tool() -> str:
    return "result"
```

## Links to Documentation

- Python: [Tools Overview](https://docs.langchain.com/oss/python/langchain/tools) | [Tool Integrations](https://docs.langchain.com/oss/python/integrations/tools/index)
- TypeScript: [Tools Overview](https://docs.langchain.com/oss/javascript/langchain/tools) | [Tool Integrations](https://docs.langchain.com/oss/javascript/integrations/tools/index)
