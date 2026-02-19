---
name: LangChain Tools Integration (Python)
description: "[LangChain] Guide to using tool integrations in LangChain including pre-built toolkits, Tavily, Wikipedia, and custom tools"
---

<overview>
Tools enable LLMs to interact with external systems, perform calculations, search the web, query databases, and more. They extend model capabilities beyond text generation, making agents truly actionable.

### Key Concepts

- **Tools**: Functions that agents can call to perform specific tasks
- **Tool Calling**: Models decide when and how to use tools based on user queries
- **Toolkits**: Collections of related tools
- **Tool Schema**: Describes tool parameters using Pydantic models
</overview>

<tool-selection>

| Tool/Toolkit | Best For | Package | Key Features |
|--------------|----------|---------|--------------|
| **Tavily Search** | Web search | `langchain-community` | AI-optimized search API |
| **Wikipedia** | Encyclopedia queries | `langchain-community` | Wikipedia API access |
| **DuckDuckGo Search** | Privacy-focused search | `langchain-community` | No API key needed |
| **ArXiv** | Academic papers | `langchain-community` | Research paper search |
| **Vector Store Tools** | Semantic search | Based on vector store | Query your data |
| **Custom Tools** | Your specific needs | `langchain-core` | Define any function |

</tool-selection>

<when-to-choose>
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
</when-to-choose>

<ex-tavily-search-tool>
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
</ex-tavily-search-tool>

<ex-wikipedia-tool>
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
</ex-wikipedia-tool>

<ex-duckduckgo-search>
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
</ex-duckduckgo-search>

<ex-arxiv-tool>
```python
from langchain_community.tools import ArxivQueryRun

arxiv_tool = ArxivQueryRun()

# Search academic papers
results = arxiv_tool.invoke("large language models")
print(results)
```
</ex-arxiv-tool>

<ex-custom-tool-decorator>
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
</ex-custom-tool-decorator>

<ex-custom-tool-pydantic-schema>
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
</ex-custom-tool-pydantic-schema>

<ex-custom-tool-class-based>
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
</ex-custom-tool-class-based>

<ex-vector-store-as-tool>
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
</ex-vector-store-as-tool>

<ex-multiple-tools>
```python
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Define tools
search_tool = TavilySearchResults(max_results=3)

@tool
def calculator(a: float, b: float, op: str) -> str:
    """Perform a mathematical operation.

    Args:
        a: First number
        b: Second number
        op: Operation to perform (add, subtract, multiply, divide)
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else float('inf')}
    result = ops.get(op)
    if result is None:
        return f"Error: Unknown operation '{op}'"
    return str(result)

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
</ex-multiple-tools>

<ex-tool-with-error-handling>
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
</ex-tool-with-error-handling>

<ex-toolkits>
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
</ex-toolkits>

<boundaries>
### What Agents CAN Do

* Use pre-built tools**
- Tavily search, Wikipedia, DuckDuckGo
- ArXiv, calculators, web browsers
- Any tool from LangChain community

* Create custom tools**
- Define functions with @tool decorator
- Implement class-based tools
- Convert retrievers to tools

* Combine multiple tools**
- Give agents access to many tools
- Let models choose appropriate tools
- Chain tool calls

* Handle tool responses**
- Parse tool output
- Use results in conversation
- Error handling

### What Agents CANNOT Do

* Execute arbitrary code safely**
- Cannot run untrusted code
- Need sandboxing for code execution

* Bypass authentication**
- Tools need proper API keys
- Cannot access protected resources without credentials

* Guarantee tool selection**
- Model decides which tool to use
- Cannot force specific tool usage (without prompting)
</boundaries>

<fix-import-from-correct-package>
```python
# WRONG: OLD
from langchain.tools import WikipediaQueryRun

# CORRECT: NEW
from langchain_community.tools import WikipediaQueryRun
```
</fix-import-from-correct-package>

<fix-api-keys-required>
```python
# WRONG: Missing API key
tool = TavilySearchResults()
tool.invoke("query")  # Error!

# CORRECT: Provide API key
import os
tool = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
```
</fix-api-keys-required>

<fix-model-must-support-tools>
```python
# WRONG: Model doesn't support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This model doesn't support tools!

# CORRECT: Use tool-capable model
model = ChatOpenAI(model="gpt-4")
```
</fix-model-must-support-tools>

<fix-tool-description-matters>
```python
# WRONG: Poor description
@tool
def tool1(x: int) -> int:
    """A tool"""  # Too vague!
    return x * 2

# CORRECT: Clear, specific description
@tool
def double_number(number: int) -> int:
    """Multiply a number by 2. Use this when the user wants to double a value.

    Args:
        number: The number to double
    """
    return number * 2
```
</fix-tool-description-matters>

<fix-type-hints-required>
```python
# WRONG: Missing type hints
@tool
def my_tool(x):  # No type hints!
    return x

# CORRECT: Include type hints
@tool
def my_tool(x: str) -> str:
    """Process input.

    Args:
        x: Input string
    """
    return x.upper()
```
</fix-type-hints-required>

<links>
### Official Documentation
- [LangChain Python Tools](https://python.langchain.com/docs/integrations/tools/)
- [Custom Tools Guide](https://python.langchain.com/docs/how_to/custom_tools/)
- [Tavily](https://docs.tavily.com/)
</links>

<installation>
```bash
# Community tools
pip install langchain-community

# Specific tools
pip install tavily-python  # For Tavily
pip install wikipedia  # For Wikipedia
pip install duckduckgo-search  # For DuckDuckGo
```
</installation>
