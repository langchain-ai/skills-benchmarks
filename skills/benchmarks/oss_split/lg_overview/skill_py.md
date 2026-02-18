---
name: LangGraph Overview (Python)
description: "[LangGraph] Understanding LangGraph: A low-level orchestration framework for building stateful, long-running agents with durable execution, streaming, and human-in-the-loop capabilities"
---

<overview>
LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It is trusted by companies like Klarna, Replit, and Elastic for production agent workloads.

**Key Characteristics:**
- **Low-level control**: Direct control over agent orchestration without high-level abstractions
- **Stateful execution**: Built-in state management and persistence
- **Production-ready**: Durable execution, streaming, human-in-the-loop, and fault-tolerance
- **Framework agnostic**: Works standalone or with LangChain components
</overview>

<when-to-use-langgraph>
LangGraph is ideal when you need:
- Fine-grained control over agent orchestration
- Durable execution for long-running, stateful agents
- Complex workflows combining deterministic and agentic steps
- Production infrastructure for agent deployment
- Human-in-the-loop workflows
- Persistent state across multiple interactions

When NOT to Use LangGraph:
- Need a quick start with pre-built architectures -> Use **LangChain agents**
- Want batteries-included features (automatic compression, virtual filesystem) -> Use **Deep Agents**
- Have simple, stateless LLM workflows -> Use **LangChain LCEL**
- Don't need state persistence or complex orchestration
</when-to-use-langgraph>

<choosing-the-right-tool>
| Requirement | Use LangGraph | Use LangChain | Use Deep Agents |
|------------|---------------|---------------|-----------------|
| Quick prototyping | No | Yes | Yes |
| Custom orchestration logic | Yes | No | Partial (limited) |
| Durable execution | Yes | Partial (via LangGraph) | Yes |
| Human-in-the-loop | Yes | Partial (via LangGraph) | Yes |
| State persistence | Yes | No | Yes |
| Production deployment | Yes | Partial (use with LangGraph) | Yes |
| Learning curve | High | Low | Medium |
</choosing-the-right-tool>

<key-concepts>
### 1. Graph-Based Execution Model

LangGraph models agent workflows as **graphs** with three core components:

- **State**: Shared data structure representing the current snapshot of your application
- **Nodes**: Functions that encode agent logic and update state
- **Edges**: Determine which node executes next (can be conditional or fixed)

### 2. Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Durable Execution** | Agents persist through failures and resume from checkpoints |
| **Streaming** | Real-time updates during execution (state, tokens, custom data) |
| **Human-in-the-loop** | Pause execution for human review and intervention |
| **Persistence** | Thread-level and cross-thread state management |
| **Time Travel** | Resume from any checkpoint in execution history |

### 3. Message Passing Model

Inspired by Google's Pregel system:
- Execution proceeds in discrete "super-steps"
- Nodes execute in parallel within a super-step
- Sequential nodes belong to separate super-steps
- Graph terminates when all nodes are inactive
</key-concepts>

<ex-basic-langgraph-agent>
```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

# 1. Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# 2. Initialize model with tools
model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)
tools = [add, multiply]
model_with_tools = model.bind_tools(tools)

# 3. Define state
class MessagesState(TypedDict):
    messages: Annotated[list, operator.add]
    llm_calls: int

# 4. Define nodes
def llm_call(state: dict):
    """LLM decides whether to call a tool or not."""
    return {
        "messages": [
            model_with_tools.invoke([
                SystemMessage(content="You are a helpful assistant."),
                *state["messages"]
            ])
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Execute tool calls."""
    result = []
    tools_by_name = {tool.name: tool for tool in tools}
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# 5. Define routing logic
def should_continue(state: MessagesState):
    """Route to tool_node or END."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return END

# 6. Build and compile graph
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    .add_edge("tool_node", "llm_call")
    .compile()
)

# 7. Invoke the agent
messages = agent.invoke({"messages": [HumanMessage(content="What is 3 * 4?")]})
for m in messages["messages"]:
    m.pretty_print()
```
</ex-basic-langgraph-agent>

<ex-agent-with-persistence>
```python
from langgraph.checkpoint.memory import InMemorySaver

# Create checkpointer for state persistence
checkpointer = InMemorySaver()

# Compile with checkpointer
agent = (
    StateGraph(MessagesState)
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue)
    .add_edge("tool_node", "llm_call")
    .compile(checkpointer=checkpointer)  # Add checkpointer
)

# First conversation turn
config = {"configurable": {"thread_id": "1"}}
agent.invoke(
    {"messages": [HumanMessage(content="Hi, I'm Alice")]},
    config
)

# Second turn - agent remembers context
agent.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config
)
```
</ex-agent-with-persistence>

<ex-streaming-agent-responses>
```python
# Stream state updates
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Calculate 5 + 3")]},
    stream_mode="updates"
):
    print(chunk)

# Stream LLM tokens
for chunk in agent.stream(
    {"messages": [HumanMessage(content="Hello!")]},
    stream_mode="messages"
):
    print(chunk)

# Multiple stream modes
for mode, chunk in agent.stream(
    {"messages": [HumanMessage(content="Help me")]},
    stream_mode=["updates", "messages"]
):
    print(f"{mode}: {chunk}")
```
</ex-streaming-agent-responses>

<boundaries>
### What Agents CAN Configure/Control

* Node Logic**: Define any Python function as a node
* State Schema**: Customize state structure and reducers
* Control Flow**: Add conditional edges, loops, branching
* Persistence Layer**: Choose checkpointer (InMemory, SQLite, Postgres)
* Streaming Modes**: Configure what data to stream
* Interrupts**: Add human-in-the-loop at any point
* Recursion Limits**: Control maximum execution steps
* Tools and Models**: Use any LLM or tool provider

### What Agents CANNOT Configure/Control

* Core Graph Execution Model**: Pregel-based runtime is fixed
* Super-step Behavior**: Cannot change how nodes are batched
* Message Passing Protocol**: Internal communication is predefined
* Checkpoint Schema**: Internal checkpoint format is fixed
* Graph Compilation**: Cannot modify compilation logic
</boundaries>

<fix-thread-ids-required-for-persistence>
```python
# WRONG: WRONG - No thread_id with checkpointer
agent.invoke({"messages": [...]})  # State not persisted!

# CORRECT: CORRECT - Always provide thread_id
agent.invoke(
    {"messages": [...]},
    {"configurable": {"thread_id": "user-123"}}
)
```
</fix-thread-ids-required-for-persistence>

<fix-state-updates-require-reducers>
```python
# WRONG: WRONG - Messages will be overwritten, not appended
class State(TypedDict):
    messages: list  # No reducer!

# CORRECT: CORRECT - Use reducer to append
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]  # Appends messages
```
</fix-state-updates-require-reducers>

<fix-compile-before-using>
```python
# WRONG: WRONG - StateGraph is not executable
builder = StateGraph(State).add_node("node", func)
builder.invoke(...)  # Error!

# CORRECT: CORRECT - Must compile first
graph = builder.compile()
graph.invoke(...)
```
</fix-compile-before-using>

<fix-infinite-loops-need-termination>
```python
# WRONG: WRONG - Loop without exit condition
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # Infinite loop!

# CORRECT: CORRECT - Add conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
</fix-infinite-loops-need-termination>

<fix-langgraph-vs-langchain-confusion>
```python
# LangChain (high-level, quick start)
from langchain.agents import create_agent
agent = create_agent(model, tools=[...])  # Simple, opinionated

# LangGraph (low-level, full control)
from langgraph.graph import StateGraph
graph = StateGraph(...).add_node(...).compile()  # More code, more control
```
</fix-langgraph-vs-langchain-confusion>

<installation>
```bash
# Python
pip install -U langgraph

# With LangChain (optional but common)
pip install -U langchain

# Production persistence
pip install -U langgraph-checkpoint-postgres
```
</installation>

<links>
- [LangGraph Overview (Python)](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [Graph API Reference](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Persistence Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Streaming Guide](https://docs.langchain.com/oss/python/langgraph/streaming)
- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)
</links>
