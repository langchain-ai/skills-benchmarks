---
name: langchain-agents
description: Build LangChain agents with modern patterns. Covers create_agent, LangGraph, and context management.
---

<oneliner>
Build production-ready agents with LangGraph, from basic primitives to advanced context management.
</oneliner>

<quick_start>
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

**Custom control flow / multi-agent / advanced context?** → **LangGraph** (see below)
**Use this for:** Custom routing logic, supervisor patterns, specialized state management, non-standard workflows.

**Start simple:** Build with basic ReAct loops first. Only add complexity when your use case requires it.
</quick_start>

<create_agent>
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
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
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
    }
    factor = conversions.get((from_unit, to_unit), None)
    return f"{value * factor:.2f} {to_unit}" if factor else "Conversion not supported"

agent = create_agent(
    model=ChatAnthropic(model="claude-sonnet-4-5"),
    tools=[calculate, convert_units],
    system_prompt="You are a helpful calculator assistant."
)
```

### Quick Reference

```python
from langchain.agents import create_agent
agent = create_agent(model=model, tools=[my_tool], system_prompt="...")
result = agent.invoke({"messages": [("user", "question")]})
```
</create_agent>

<langgraph>
### Basic Agent from Scratch

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

tools = [search_tool]
tool_node = ToolNode(tools)

def agent(state: State):
    return {"messages": [model.bind_tools(tools).invoke(state["messages"])]}

def route(state: State):
    return "tools" if state["messages"][-1].tool_calls else END

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
    if needs_more_context(state):
        return Command(update={"notes": "Starting research"}, goto="research")
    return Command(goto=END)

# Human-in-loop
def ask_user(state: State) -> Command:
    response = interrupt("Please clarify:")
    return Command(update={"messages": [HumanMessage(content=response)]}, goto="continue")
```
</langgraph>

<context_management>
### Strategy 1: Subagent Delegation

**Pattern:** Offload work to subagents, return only summaries.

```python
researcher_subgraph = build_researcher_graph().compile()

def main_agent(state: State) -> Command:
    if needs_research(state["messages"][-1]):
        result = researcher_subgraph.invoke({"query": extract_query(state)})
        return Command(
            update={"context": state["context"] + f"\n{result['summary']}"},
            goto="respond"
        )
    return Command(goto="respond")
```

### Strategy 2: Progressive Message Trimming

**Pattern:** Remove old messages but preserve system messages and recent context.

```python
def trim_messages(messages: list, max_messages: int = 20) -> list:
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    conversation = [m for m in messages if not isinstance(m, SystemMessage)]
    return system_msgs + conversation[-max_messages:]

def agent_with_trimming(state: State) -> dict:
    trimmed = trim_messages(state["messages"], max_messages=15)
    return {"messages": [model.invoke(trimmed)]}
```

### Strategy 3: Compression with Summarization

**Pattern:** Summarize old context, keep recent messages raw.

```python
def compress_history(state: State) -> dict:
    messages = state["messages"]
    if len(messages) > 30:
        old, recent = messages[:-10], messages[-10:]
        summary = model.invoke([HumanMessage(content=f"Summarize:\n{format_messages(old)}")])
        return {"messages": [SystemMessage(content=f"Previous:\n{summary.content}")] + recent}
    return {"messages": messages}
```
</context_management>

<multi_agent>
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
    last_msg = state["messages"][-1].content.lower()
    if "invoice" in last_msg or "payment" in last_msg:
        return Command(goto="billing")
    elif "error" in last_msg or "not working" in last_msg:
        return Command(goto="technical")
    return Command(goto=END)

def billing_agent(state: AgentState) -> dict:
    return {"messages": [billing_model.invoke(state["messages"])]}

def technical_agent(state: AgentState) -> dict:
    return {"messages": [tech_model.invoke(state["messages"])]}

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("billing", billing_agent)
workflow.add_node("technical", technical_agent)
workflow.add_edge(START, "supervisor")
workflow.add_edge("billing", END)
workflow.add_edge("technical", END)
app = workflow.compile()
```
</multi_agent>

<advanced>
### Persistence with Checkpointer + Store

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = MemorySaver()  # Thread-level state
store = InMemoryStore()       # Cross-thread memory

app = graph.compile(checkpointer=checkpointer, store=store)

app.invoke(
    {"messages": [HumanMessage("Hello")]},
    config={"configurable": {"thread_id": "user-123"}}
)
```

### Structured Output

```python
from pydantic import BaseModel, Field

class ResearchOutput(BaseModel):
    summary: str = Field(description="3-sentence summary")
    sources: list[str] = Field(description="Source URLs")
    confidence: float = Field(description="0-1 confidence score")

model_with_structure = model.with_structured_output(ResearchOutput)

def structured_research(state: State) -> dict:
    result = model_with_structure.invoke(state["messages"])
    return {"research": result.model_dump()}
```

### DeepAgents: Batteries Included

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend

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

**DeepAgents provides:** Filesystem (auto context files), Planning (task breakdown), Subagents (delegation), Memory (persistence).
</advanced>

<resources>
- [LangGraph Docs](https://docs.langchain.com/langgraph)
- [create_agent](https://docs.langchain.com/oss/python/langchain/agents)
- [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph 101 Multi-Agent](https://github.com/langchain-ai/langgraph-101/blob/main/notebooks/LG201/multi_agent.ipynb)
- [Deep Research Example](https://github.com/langchain-samples/deep_research_101)
</resources>
