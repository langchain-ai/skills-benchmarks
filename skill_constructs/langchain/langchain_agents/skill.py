"""LangChain Agents skill sections.

Each section is a string that can be assembled into a complete skill.
Test cases in templates.py define which sections to use and can substitute custom content.
"""

FRONTMATTER = """---
name: langchain-agents
description: Build LangChain agents with modern patterns. Covers create_agent, LangGraph, and context management.
---"""

HEADER = """# LangChain Ecosystem Guide

Build production-ready agents with LangGraph, from basic primitives to advanced context management."""

QUICK_START = """## Quick Start: Which Tool?"""

# This is the default guidance - tests can substitute their own
GUIDANCE = """**IMPORTANT:** Use modern abstractions. Older helpers like `create_sql_agent`, `create_tool_calling_agent`, `create_react_agent`, etc. are outdated."""

CREATE_AGENT_OVERVIEW = """**Simple tool-calling agent?** → [`create_agent`](https://docs.langchain.com/oss/python/langchain/agents)
```python
from langchain.agents import create_agent
graph = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search], system_prompt="...")
```
**Use this for:** Basic ReAct loops, tool-calling agents, simple Q&A bots."""

DEEP_AGENT_OVERVIEW = """**Need planning + filesystem + subagents?** → [`create_deep_agent`](https://docs.langchain.com/oss/python/deepagents/overview)
```python
from deepagents import create_deep_agent
agent = create_deep_agent(model=model, tools=tools, backend=FilesystemBackend())
```
**Use this for:** Research agents, complex workflows, multi-step planning."""

LANGGRAPH_OVERVIEW = """**Custom control flow / multi-agent?** → **LangGraph** (this guide)
**Use this for:** Custom routing logic, supervisor patterns, specialized state management.

**Start simple:** Build with basic ReAct loops first. Only add complexity when needed."""

CREATE_AGENT_EXAMPLE = """## Core Primitives

### Using create_agent (Recommended)

```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    \"\"\"Tool description that the model sees.\"\"\"
    return perform_operation(query)

model = ChatAnthropic(model="claude-sonnet-4-5")
agent = create_agent(
    model=model,
    tools=[my_tool],
    system_prompt="Your agent behavior and guidelines."
)

result = agent.invoke({"messages": [("user", "Your question")]})
```

**Pattern applies to:** SQL agents, search agents, Q&A bots, tool-calling workflows."""

SQL_EXAMPLE = """### Example: SQL Agent (Text-to-SQL)

```python
import sqlite3
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.tools import tool

def get_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = "\\n".join([row[0] for row in cursor.fetchall()])
    conn.close()
    return schema

@tool
def query_database(sql_query: str) -> str:
    \"\"\"Execute a SQL SELECT query and return results.\"\"\"
    if not sql_query.upper().strip().startswith("SELECT"):
        return "Error: Only SELECT queries allowed"
    conn = sqlite3.connect("chinook.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()
    return str(results)

schema = get_schema("chinook.db")
model = ChatAnthropic(model="claude-sonnet-4-5")
agent = create_agent(
    model=model,
    tools=[query_database],
    system_prompt=f"You are a SQL expert. Generate SELECT queries.\\n\\nSchema:\\n{schema}"
)

result = agent.invoke({"messages": [("user", "How many customers are there?")]})
```"""

QUICK_REFERENCE = """## Quick Reference

```python
# Create agent
from langchain.agents import create_agent
agent = create_agent(model=model, tools=[my_tool], system_prompt="...")

# Define tools
@tool
def my_tool(query: str) -> str:
    \"\"\"Description the model sees.\"\"\"
    return result

# Invoke
result = agent.invoke({"messages": [("user", "question")]})
```"""

# Default section order for assembly
DEFAULT_SECTIONS = [
    FRONTMATTER,
    HEADER,
    QUICK_START,
    GUIDANCE,
    CREATE_AGENT_OVERVIEW,
    DEEP_AGENT_OVERVIEW,
    LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE,
    SQL_EXAMPLE,
    QUICK_REFERENCE,
]
