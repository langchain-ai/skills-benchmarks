---
name: langchain-agents
description: Build LangChain agents with modern patterns. Covers create_agent, LangGraph, and context management.
---

# LangChain Ecosystem Guide

Build production-ready agents with LangGraph, from basic primitives to advanced context management.

## Quick Start: Which Tool?

**IMPORTANT:** Use modern abstractions. Older helpers like `create_sql_agent`, `create_tool_calling_agent`, `create_react_agent`, etc. are outdated.

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

**Custom control flow / multi-agent / advanced context?** → **LangGraph** (this guide)
**Use this for:** Custom routing logic, supervisor patterns, specialized state management, non-standard workflows.

**Start simple:** Build with basic ReAct loops first. Only add complexity (multi-agent, advanced context management) when your use case requires it.

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

### Basic Agent from Scratch

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

tools = [search_tool]
tool_node = ToolNode(tools)  # Handles ToolMessage generation

def agent(state: State):
    return {"messages": [model.bind_tools(tools).invoke(state["messages"])]}

def route(state: State):
    return "tools" if state["messages"][-1].tool_calls else END

# Build graph
workflow = StateGraph(State)
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", route)
workflow.add_edge("tools", "agent")
app = workflow.compile()
```

**The loop:** Agent → tools → agent → END

### ToolMessages: Critical Detail

When implementing custom tool execution, you **must** create a `ToolMessage` for each tool call:

```python
from langchain_core.messages import ToolMessage

def custom_tool_node(state: State) -> dict:
    """Execute tools manually."""
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        result = execute_tool(tool_call["name"], tool_call["args"])

        # CRITICAL: tool_call_id must match!
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))

    return {"messages": tool_messages}
```

### Commands: Routing with Updates

```python
from langgraph.types import Command
from typing import Literal

def router(state: State) -> Command[Literal["research", "write", END]]:
    """Route and update state simultaneously."""
    if needs_more_context(state):
        return Command(
            update={"notes": "Starting research phase"},
            goto="research"
        )
    return Command(goto=END)

# Human-in-loop: pause and resume
def ask_user(state: State) -> Command:
    response = interrupt("Please clarify:")
    return Command(
        update={"messages": [HumanMessage(content=response)]},
        goto="continue"
    )

# Resume: graph.invoke(Command(resume=user_input), config)
```

## Context Management Strategies

### Strategy 1: Subagent Delegation

**Pattern:** Offload work to subagents, return only summaries.

```python
# Specialized subagent (compiles full workflow internally)
researcher_subgraph = build_researcher_graph().compile()

# Main agent delegates
def main_agent(state: State) -> Command:
    if needs_research(state["messages"][-1]):
        result = researcher_subgraph.invoke({"query": extract_query(state)})
        # Add ONLY summary to main context
        return Command(
            update={"context": state["context"] + f"\n{result['summary']}"},
            goto="respond"
        )
    return Command(goto="respond")
```

**Why:** Subagent handles complexity, main agent only sees compressed summary.

### Strategy 2: Progressive Message Trimming

**Pattern:** Remove old messages but preserve recent context and critical system messages.

```python
def trim_messages(messages: list, max_messages: int = 20) -> list:
    """Keep system messages + recent conversation."""
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    conversation = [m for m in messages if not isinstance(m, SystemMessage)]
    recent = conversation[-max_messages:]
    return system_msgs + recent

def agent_with_trimming(state: State) -> dict:
    """Call model with trimmed context."""
    trimmed = trim_messages(state["messages"], max_messages=15)
    response = model.invoke(trimmed)
    return {"messages": [response]}
```

### Strategy 3: Compression with Summarization

**Pattern:** Summarize old context into compact form, keep only recent messages raw.

```python
def compress_history(state: State) -> dict:
    """Compress old messages into summary."""
    messages = state["messages"]

    if len(messages) > 30:
        old_messages = messages[:-10]
        recent_messages = messages[-10:]

        summary_prompt = f"Summarize this conversation history concisely:\n{format_messages(old_messages)}"
        summary = model.invoke([HumanMessage(content=summary_prompt)])

        compressed = [
            SystemMessage(content=f"Previous context:\n{summary.content}")
        ] + recent_messages

        return {"messages": compressed}

    return {"messages": messages}
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

## Practical Patterns

### Checkpointer + Store for Persistence

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = MemorySaver()  # Thread-level state
store = InMemoryStore()       # Cross-thread memory

app = graph.compile(
    checkpointer=checkpointer,  # Enables conversation continuity
    store=store                  # Enables learning across conversations
)

# Thread-specific conversation
app.invoke(
    {"messages": [HumanMessage("Hello")]},
    config={"configurable": {"thread_id": "user-123"}}
)
```

### Structured Output for Reliability

```python
from pydantic import BaseModel, Field

class ResearchOutput(BaseModel):
    summary: str = Field(description="3-sentence summary")
    sources: list[str] = Field(description="Source URLs")
    confidence: float = Field(description="0-1 confidence score")

model_with_structure = model.with_structured_output(ResearchOutput)

def structured_research(state: State) -> dict:
    result = model_with_structure.invoke(state["messages"])
    # result is guaranteed to have summary, sources, confidence
    return {"research": result.model_dump()}
```

## DeepAgents: Batteries Included

When you need context management built-in:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend

# Mix filesystem (working files) + store (memories)
backend = CompositeBackend({
    "/workspace/": FilesystemBackend("./workspace"),
    "/memories/": StoreBackend(store)
})

agent = create_deep_agent(
    model=model,
    tools=[search, scrape],
    subagents=[researcher_agent, analyst_agent],
    backend=backend
)
```

**DeepAgents provides:**
- Filesystem: Write/read context files automatically
- Planning: Break tasks into steps
- Subagents: Delegate to specialists
- Memory: Persistent storage across sessions

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

## Resources

- [LangGraph Docs](https://docs.langchain.com/langgraph)
- [create_agent](https://docs.langchain.com/oss/python/langchain/agents)
- [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph 101 Multi-Agent](https://github.com/langchain-ai/langgraph-101/blob/main/notebooks/LG201/multi_agent.ipynb)
- [Deep Research Example](https://github.com/langchain-samples/deep_research_101)