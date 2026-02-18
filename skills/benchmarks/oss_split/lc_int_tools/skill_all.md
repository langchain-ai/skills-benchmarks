---
name: LangChain Tools Integration
description: "[LangChain] Guide to using tool integrations in LangChain including pre-built toolkits, Tavily, Wikipedia, and custom tools"
---

## Overview

Tools enable LLMs to interact with external systems, perform calculations, search the web, query databases, and more. They extend model capabilities beyond text generation, making agents truly actionable.

### Key Concepts

- **Tools**: Functions that agents can call to perform specific tasks
- **Tool Calling**: Models decide when and how to use tools based on user queries
- **Toolkits**: Collections of related tools
- **Tool Schema**: Describes tool parameters using Pydantic models (Python) or Zod/JSON Schema (TypeScript)

## Tool Selection Decision Table

| Tool/Toolkit | Best For | Package (Python / TypeScript) | Key Features |
|--------------|----------|-------------------------------|--------------|
| **Tavily Search** | Web search | `langchain-community` / `@langchain/community` | AI-optimized search API |
| **Wikipedia** | Encyclopedia queries | `langchain-community` / `@langchain/community` | Wikipedia API access |
| **Calculator** | Math operations | `langchain-community` / `@langchain/community` | Expression evaluation |
| **DuckDuckGo Search** | Privacy-focused search | `langchain-community` / `@langchain/community` | No API key needed |
| **ArXiv** | Academic papers | `langchain-community` | Research paper search (Python) |
| **Vector Store Tools** | Semantic search | Based on vector store | Query your data |
| **Custom Tools** | Your specific needs | `langchain-core` / `@langchain/core/tools` | Define any function |

### When to Choose Each Tool

**Choose Tavily if:**
- You need high-quality web search
- You want AI-optimized results
- You're building research/RAG applications

**Choose Wikipedia if:**
- You need encyclopedic knowledge
- Factual information is required
- Free, no API key needed

**Choose Custom Tools if:**
- You have specific business logic
- You need to integrate proprietary systems
- Built-in tools don't meet your needs

## Code Examples

### Tavily Search Tool

#### Python

```python
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# Initialize Tavily (requires API key)
search_tool = TavilySearchResults(
    max_results=3,
    api_key=os.getenv("TAVILY_API_KEY"),
)

# Use directly
results = search_tool.invoke("Latest AI news")
print(results)

# Use with agent
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="gpt-4")
agent = create_react_agent(model, [search_tool])

response = agent.invoke({
    "messages": [{"role": "user", "content": "What's new in AI today?"}]
})
```

#### TypeScript

```typescript
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";

// Initialize Tavily (requires API key)
const searchTool = new TavilySearchResults({
  maxResults: 3,
  apiKey: process.env.TAVILY_API_KEY,
});

// Use directly
const results = await searchTool.invoke("Latest AI news");
console.log(results);

// Use with agent
import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const model = new ChatOpenAI({ modelName: "gpt-4" });
const agent = createReactAgent({
  llm: model,
  tools: [searchTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's new in AI today?" }]
});
```

### Wikipedia Tool

#### Python

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000,
    )
)

# Query Wikipedia
result = wikipedia.invoke("Artificial Intelligence")
print(result)
```

#### TypeScript

```typescript
import { WikipediaQueryRun } from "@langchain/community/tools/wikipedia_query_run";

const wikipediaTool = new WikipediaQueryRun({
  topKResults: 3,
  maxDocContentLength: 4000,
});

// Query Wikipedia
const result = await wikipediaTool.invoke("Artificial Intelligence");
console.log(result);
```

### Calculator Tool (TypeScript)

```typescript
import { Calculator } from "@langchain/community/tools/calculator";

const calculator = new Calculator();

// Perform calculations
const result = await calculator.invoke("sqrt(144) + 5 * 3");
console.log(result); // "27"

// Use in agent for math problems
const mathAgent = createReactAgent({
  llm: model,
  tools: [calculator],
});
```

### DuckDuckGo Search (No API Key)

#### Python

```python
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

results = search_tool.invoke("LangChain framework")
print(results)

# With results object for more details
from langchain_community.tools import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(max_results=5)
results = search_tool.invoke("Python programming")
```

#### TypeScript

```typescript
import { DuckDuckGoSearch } from "@langchain/community/tools/duckduckgo_search";

const searchTool = new DuckDuckGoSearch({
  maxResults: 5,
});

const results = await searchTool.invoke("LangChain framework");
```

### ArXiv Tool (Python)

```python
from langchain_community.tools import ArxivQueryRun

arxiv_tool = ArxivQueryRun()

# Search academic papers
results = arxiv_tool.invoke("large language models")
print(results)
```

### Custom Tool with Decorator/Function

#### Python

```python
from langchain_core.tools import tool
from typing import Optional

@tool
def get_weather(location: str, unit: Optional[str] = "celsius") -> str:
    """Get the current weather for a location.

    Args:
        location: The city name, e.g., 'San Francisco'
        unit: Temperature unit, either 'celsius' or 'fahrenheit'
    """
    # Your implementation
    data = fetch_weather(location, unit)
    return f"The weather in {location} is {data['temp']}°{unit[0].upper()}"

# Use with agent
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="gpt-4")
agent = create_react_agent(model, [get_weather])

response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in London?"}]
})
```

#### TypeScript

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// Define custom tool
const weatherTool = tool(
  async ({ location, unit = "celsius" }) => {
    // Your implementation
    const data = await fetchWeather(location, unit);
    return `The weather in ${location} is ${data.temp}°${unit === "celsius" ? "C" : "F"}`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location. Use this when users ask about weather.",
    schema: z.object({
      location: z.string().describe("The city name, e.g., 'San Francisco'"),
      unit: z.enum(["celsius", "fahrenheit"]).optional().describe("Temperature unit"),
    }),
  }
);

// Use with agent
const agent = createReactAgent({
  llm: model,
  tools: [weatherTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in London?" }]
});
```

### Custom Tool with Pydantic Schema (Python)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="The city name")
    unit: str = Field(default="celsius", description="Temperature unit")

@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather for a location."""
    # Implementation
    return f"Weather in {location}: 72°{unit[0].upper()}"

# Tool now has proper schema validation
```

### Custom Tool - Class-Based

#### Python

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

#### TypeScript

```typescript
import { StructuredTool } from "@langchain/core/tools";
import { z } from "zod";

class DatabaseQueryTool extends StructuredTool {
  name = "database_query";
  description = "Query the customer database for information";

  schema = z.object({
    customerId: z.string().describe("Customer ID to look up"),
  });

  async _call({ customerId }: { customerId: string }): Promise<string> {
    // Your database logic
    const customer = await db.getCustomer(customerId);
    return JSON.stringify(customer);
  }
}

const dbTool = new DatabaseQueryTool();
```

### Vector Store as Tool

#### Python

```python
from langchain_core.tools import create_retriever_tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# Create vector store
vectorstore = InMemoryVectorStore.from_texts(
    ["LangChain is a framework...", "Agents use tools..."],
    embedding=OpenAIEmbeddings(),
)

# Convert to tool
retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="knowledge_base",
    description="Search the knowledge base for information about LangChain",
)

# Use in agent
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, [retriever_tool])
```

#### TypeScript

```typescript
import { createRetrieverTool } from "langchain/tools/retriever";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

// Create vector store
const vectorStore = await MemoryVectorStore.fromTexts(
  ["LangChain is a framework...", "Agents use tools..."],
  [{}, {}],
  new OpenAIEmbeddings()
);

// Convert to tool
const retrieverTool = createRetrieverTool(
  vectorStore.asRetriever(),
  {
    name: "knowledge_base",
    description: "Search the knowledge base for information about LangChain",
  }
);

// Use in agent
const agent = createReactAgent({
  llm: model,
  tools: [retrieverTool],
});
```

### Multiple Tools Example

#### Python

```python
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Define tools
search_tool = TavilySearchResults(max_results=3)

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2")
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def custom_lookup(query: str) -> str:
    """Look up custom information.

    Args:
        query: The query to look up
    """
    # Your custom logic
    return f"Custom result for: {query}"

# Create agent with multiple tools
agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    [search_tool, calculator, custom_lookup],
)

# Agent will choose appropriate tool(s)
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Search for the population of Tokyo and calculate if it doubled"
    }]
})
```

#### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";
import { Calculator } from "@langchain/community/tools/calculator";
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

// Define tools
const searchTool = new TavilySearchResults({ maxResults: 3 });
const calculator = new Calculator();

const customTool = tool(
  async ({ query }) => {
    // Your custom logic
    return `Custom result for: ${query}`;
  },
  {
    name: "custom_lookup",
    description: "Look up custom information",
    schema: z.object({
      query: z.string().describe("The query to look up"),
    }),
  }
);

// Create agent with multiple tools
const agent = createReactAgent({
  llm: new ChatOpenAI({ modelName: "gpt-4" }),
  tools: [searchTool, calculator, customTool],
});

// Agent will choose appropriate tool(s)
const response = await agent.invoke({
  messages: [{
    role: "user",
    content: "Search for the population of Tokyo and calculate if it doubled"
  }]
});
```

### Tool with Error Handling

#### Python

```python
from langchain_core.tools import tool
import requests

@tool
def api_call(endpoint: str) -> str:
    """Call external API.

    Args:
        endpoint: API endpoint to call
    """
    try:
        response = requests.get(f"https://api.example.com/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"API error: {str(e)}"

# Error handling is critical for robust tools
```

#### TypeScript

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const apiTool = tool(
  async ({ endpoint }) => {
    try {
      const response = await fetch(`https://api.example.com/${endpoint}`);
      if (!response.ok) {
        return `API error: ${response.statusText}`;
      }
      const data = await response.json();
      return JSON.stringify(data);
    } catch (error) {
      return `Failed to call API: ${error.message}`;
    }
  },
  {
    name: "api_call",
    description: "Call external API",
    schema: z.object({
      endpoint: z.string().describe("API endpoint to call"),
    }),
  }
);
```

### Toolkits (Python)

```python
# SQL Database Toolkit
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///example.db")
toolkit = SQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()
# Includes: query, schema info, query checker, etc.

# Use in agent
agent = create_react_agent(model, tools)
```

## Boundaries

### What Agents CAN Do

- **Use pre-built tools** - Tavily search, Wikipedia, DuckDuckGo, ArXiv, calculators, web browsers, any tool from LangChain community
- **Create custom tools** - Define functions with @tool decorator (Python) or tool() (TypeScript), implement class-based tools, convert retrievers to tools
- **Combine multiple tools** - Give agents access to many tools, let models choose appropriate tools, chain tool calls
- **Handle tool responses** - Parse tool output, use results in conversation, error handling

### What Agents CANNOT Do

- **Execute arbitrary code safely** - Cannot run untrusted code; need sandboxing for code execution
- **Bypass authentication** - Tools need proper API keys; cannot access protected resources without credentials
- **Guarantee tool selection** - Model decides which tool to use; cannot force specific tool usage (without prompting)
- **Use tools model doesn't support** - Not all models support tool calling; need GPT-4, Claude 3, or similar

## Gotchas

### 1. Import from Correct Package (Python)

```python
# ❌ OLD
from langchain.tools import WikipediaQueryRun

# ✅ NEW
from langchain_community.tools import WikipediaQueryRun
```

**Fix**: Use `langchain-community` for tools.

### 2. API Keys Required

#### Python

```python
# ❌ Missing API key
tool = TavilySearchResults()
tool.invoke("query")  # Error!

# ✅ Provide API key
import os
tool = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
```

#### TypeScript

```typescript
// ❌ Missing API key
const tool = new TavilySearchResults();
await tool.invoke("query"); // Error!

// ✅ Provide API key
const tool = new TavilySearchResults({
  apiKey: process.env.TAVILY_API_KEY,
});
```

**Fix**: Set required API keys in environment variables.

### 3. Model Must Support Tools

#### Python

```python
# ❌ Model doesn't support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This model doesn't support tools!

# ✅ Use tool-capable model
model = ChatOpenAI(model="gpt-4")
```

#### TypeScript

```typescript
// ❌ Model doesn't support tool calling
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This model doesn't support tools!

// ✅ Use tool-capable model
const model = new ChatOpenAI({ modelName: "gpt-4" });
const modelWithTools = model.bindTools([myTool]);
```

**Fix**: Use models that support function calling (GPT-4, Claude 3, etc.).

### 4. Tool Description Matters

#### Python

```python
# ❌ Poor description
@tool
def tool1(x: int) -> int:
    """A tool"""  # Too vague!
    return x * 2

# ✅ Clear, specific description
@tool
def double_number(number: int) -> int:
    """Multiply a number by 2. Use this when the user wants to double a value.

    Args:
        number: The number to double
    """
    return number * 2
```

#### TypeScript

```typescript
// ❌ Poor description
const myTool = tool(
  async ({ x }) => x * 2,
  {
    name: "tool1",
    description: "A tool", // Too vague!
    schema: z.object({ x: z.number() }),
  }
);

// ✅ Clear, specific description
const myTool = tool(
  async ({ number }) => number * 2,
  {
    name: "double_number",
    description: "Multiply a number by 2. Use this when the user wants to double a value.",
    schema: z.object({
      number: z.number().describe("The number to double"),
    }),
  }
);
```

**Fix**: Write clear descriptions that help the model know when to use the tool.

### 5. Type Hints Required (Python)

```python
# ❌ Missing type hints
@tool
def my_tool(x):  # No type hints!
    return x

# ✅ Include type hints
@tool
def my_tool(x: str) -> str:
    """Process input.

    Args:
        x: Input string
    """
    return x.upper()
```

**Fix**: Always include type hints for tool parameters.

### 6. Schema Validation (TypeScript)

```typescript
// ❌ No schema validation
const myTool = tool(
  async ({ location }) => {
    // Assumes location is a string, but no validation
    return location.toUpperCase(); // Could crash!
  },
  {
    name: "format_location",
    description: "Format location",
    schema: z.object({ location: z.any() }), // Too permissive
  }
);

// ✅ Proper schema
const myTool = tool(
  async ({ location }) => {
    return location.toUpperCase();
  },
  {
    name: "format_location",
    description: "Format location name to uppercase",
    schema: z.object({
      location: z.string().describe("Location name"),
    }),
  }
);
```

**Fix**: Use specific Zod schemas for type safety.

## Links to Documentation

### Python
- [LangChain Python Tools](https://python.langchain.com/docs/integrations/tools/)
- [Custom Tools Guide](https://python.langchain.com/docs/how_to/custom_tools/)

### TypeScript
- [LangChain JS Tools](https://js.langchain.com/docs/integrations/tools/)
- [Custom Tools Guide](https://js.langchain.com/docs/how_to/custom_tools/)

### External
- [Tavily](https://docs.tavily.com/)

### Package Installation

**Python:**
```bash
# Community tools
pip install langchain-community

# Specific tools
pip install tavily-python  # For Tavily
pip install wikipedia  # For Wikipedia
pip install duckduckgo-search  # For DuckDuckGo
```

**TypeScript:**
```bash
# Community tools
npm install @langchain/community

# Core tools
npm install @langchain/core

# Specific integrations
npm install @langchain/openai  # For OpenAI-based tools
```
