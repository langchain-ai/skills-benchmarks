---
name: langchain-agents
description: Build LangChain agents with modern patterns. Covers create_agent, LangGraph, and context management.
---

# LangChain Ecosystem Guide

Build production-ready agents with LangGraph, from basic primitives to advanced context management.

## Quick Start: Which Tool?

## Important: Use Modern LangChain Patterns

Use the modern approach:
- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions

See the examples below for working code.

**Simple tool-calling agent?** → [`create_agent`](https://docs.langchain.com/oss/python/langchain/agents)
```python
from langchain.agents import create_agent
graph = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search], system_prompt="...")
```
**Use this for:** Basic ReAct loops, tool-calling agents, simple Q&A bots.

**Need planning + filesystem + subagents?** → [`create_deep_agent`](https://docs.langchain.com/oss/python/deepagents/overview)
```python
from deepagents import create_deep_agent
agent = create_deep_agent(model=model, tools=tools, backend=FilesystemBackend())
```
**Use this for:** Research agents, complex workflows, multi-step planning.

**Custom control flow / multi-agent?** → **LangGraph** (this guide)
**Use this for:** Custom routing logic, supervisor patterns, specialized state management.

**Start simple:** Build with basic ReAct loops first. Only add complexity when needed.

## Core Primitives

### Using create_agent (Recommended)

```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """Tool description that the model sees."""
    return perform_operation(query)

model = ChatAnthropic(model="claude-sonnet-4-5")
agent = create_agent(
    model=model,
    tools=[my_tool],
    system_prompt="Your agent behavior and guidelines."
)

result = agent.invoke({"messages": [("user", "Your question")]})
```

**Pattern applies to:** SQL agents, search agents, Q&A bots, tool-calling workflows.

### Example: Calculator Agent

```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        # Only allow safe math operations
        allowed = set('0123456789+-*/(). ')
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters"
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units."""
    conversions = {
        ("km", "miles"): 0.621371,
        ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462,
        ("lbs", "kg"): 0.453592,
    }
    factor = conversions.get((from_unit, to_unit), None)
    if factor:
        return f"{value * factor:.2f} {to_unit}"
    return "Conversion not supported"

model = ChatAnthropic(model="claude-sonnet-4-5")
agent = create_agent(
    model=model,
    tools=[calculate, convert_units],
    system_prompt="You are a helpful calculator assistant."
)

result = agent.invoke({"messages": [("user", "What is 15% of 250?")]})
```

## Multi-Agent Patterns

### Supervisor Pattern

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str

def supervisor(state: AgentState) -> Command[Literal["billing", "technical", END]]:
    """Route to appropriate specialist based on request type."""
    last_msg = state["messages"][-1].content.lower()

    # Simple routing logic (use LLM for complex cases)
    if "invoice" in last_msg or "payment" in last_msg:
        return Command(goto="billing")
    elif "error" in last_msg or "not working" in last_msg:
        return Command(goto="technical")
    return Command(goto=END)

def billing_agent(state: AgentState) -> dict:
    """Handle billing-related queries."""
    response = billing_model.invoke(state["messages"])
    return {"messages": [response]}

def technical_agent(state: AgentState) -> dict:
    """Handle technical support queries."""
    response = tech_model.invoke(state["messages"])
    return {"messages": [response]}

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("billing", billing_agent)
workflow.add_node("technical", technical_agent)
workflow.add_edge(START, "supervisor")
workflow.add_edge("billing", END)
workflow.add_edge("technical", END)

app = workflow.compile()
print(list(app.get_graph().nodes.keys()))  # See graph structure
```

## Quick Reference

```python
# Create agent
from langchain.agents import create_agent
agent = create_agent(model=model, tools=[my_tool], system_prompt="...")

# Define tools
@tool
def my_tool(query: str) -> str:
    """Description the model sees."""
    return result

# Invoke
result = agent.invoke({"messages": [("user", "question")]})
```
