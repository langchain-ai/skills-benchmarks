---
name: langgraph-workflows
description: "[LangGraph] Understanding workflows vs agents, predetermined vs dynamic patterns, and orchestrator-worker patterns using the Send API"
---

<overview>
LangGraph supports both **workflows** (predetermined paths) and **agents** (dynamic decision-making). Understanding when to use each pattern is crucial for effective agent design.

**Key Distinctions:**
- **Workflows**: Predetermined code paths, operate in specific order
- **Agents**: Dynamic, define their own processes and tool usage
- **Hybrid**: Combine deterministic and agentic steps
</overview>

<decision-table>

| Characteristic | Workflow | Agent | Hybrid |
|----------------|----------|-------|--------|
| **Control Flow** | Fixed, predetermined | Dynamic, model-driven | Mixed |
| **Predictability** | High | Low | Medium |
| **Complexity** | Simple | Complex | Variable |
| **Use Case** | Sequential tasks | Open-ended problems | Structured flexibility |
| **Examples** | ETL, validation | Research, QA | Review approval |

</decision-table>

<key-patterns>
**1. Predetermined Workflows**

Sequential execution with fixed paths:
- Data processing pipelines
- Validation workflows
- Multi-step transformations

**2. Dynamic Agents**

Model decides next steps:
- ReAct agents (reasoning + acting)
- Tool-calling loops
- Autonomous task completion

**3. Orchestrator-Worker Pattern**

One coordinator delegates to multiple workers:
- Map-reduce operations
- Parallel processing
- Multi-agent collaboration
</key-patterns>

<ex-basic>
<python>
Fixed path workflow:

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    data: str
    validated: bool
    processed: bool

def validate(state: WorkflowState) -> dict:
    """Validate input data."""
    is_valid = len(state["data"]) > 0
    return {"validated": is_valid}

def process(state: WorkflowState) -> dict:
    """Process validated data."""
    return {
        "data": state["data"].upper(),
        "processed": True
    }

# Fixed workflow: validate -> process
workflow = (
    StateGraph(WorkflowState)
    .add_node("validate", validate)
    .add_node("process", process)
    .add_edge(START, "validate")
    .add_edge("validate", "process")  # Always go to process
    .add_edge("process", END)
    .compile()
)

result = workflow.invoke({"data": "hello"})
print(result)  # {'data': 'HELLO', 'validated': True, 'processed': True}
```
</python>

<typescript>
Fixed path workflow:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const WorkflowState = new StateSchema({
  data: z.string(),
  validated: z.boolean(),
  processed: z.boolean(),
});

const validate = async (state: typeof WorkflowState.State) => {
  const isValid = state.data.length > 0;
  return { validated: isValid };
};

const process = async (state: typeof WorkflowState.State) => {
  return {
    data: state.data.toUpperCase(),
    processed: true,
  };
};

// Fixed workflow: validate -> process
const workflow = new StateGraph(WorkflowState)
  .addNode("validate", validate)
  .addNode("process", process)
  .addEdge(START, "validate")
  .addEdge("validate", "process")  // Always go to process
  .addEdge("process", END)
  .compile();

const result = await workflow.invoke({ data: "hello" });
console.log(result);  // { data: 'HELLO', validated: true, processed: true }
```
</typescript>
</ex-basic>

<ex-agent>
<python>
Tool-calling agent with dynamic routing:

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def calculate(a: float, b: float, op: str) -> str:
    """Calculate a mathematical expression.

    Args:
        a: First number
        b: Second number
        op: Operation (add, subtract, multiply, divide)
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return str(ops.get(op, "Invalid operation"))

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

model = init_chat_model("claude-sonnet-4-5-20250929")
tools = [search, calculate]
model_with_tools = model.bind_tools(tools)

def agent_node(state: AgentState) -> dict:
    """Agent decides which tool to use (if any)."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute tools chosen by agent."""
    tools_by_name = {tool.name: tool for tool in tools}
    result = []

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: AgentState):
    """Dynamic: agent decides if it needs more tools."""
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# Dynamic agent: model decides when to stop
agent = (
    StateGraph(AgentState)
    .add_node("agent", agent_node)
    .add_node("tools", tool_node)
    .add_edge(START, "agent")
    .add_conditional_edges("agent", should_continue)  # Model decides
    .add_edge("tools", "agent")
    .compile()
)
```
</python>

<typescript>
Tool-calling agent with dynamic routing:

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";
import { AIMessage, ToolMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, END, START } from "@langchain/langgraph";
import { z } from "zod";

const search = tool(async ({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

const calculate = tool(async ({ a, b, op }) => {
  const ops: Record<string, number> = { add: a + b, subtract: a - b, multiply: a * b, divide: a / b };
  return (ops[op] ?? "Invalid operation").toString();
}, {
  name: "calculate",
  description: "Calculate a mathematical expression",
  schema: z.object({ a: z.number(), b: z.number(), op: z.string() }),
});

const AgentState = new StateSchema({
  messages: MessagesValue,
});

const model = new ChatAnthropic({ model: "claude-sonnet-4-5-20250929" });
const tools = [search, calculate];
const modelWithTools = model.bindTools(tools);

const agentNode = async (state: typeof AgentState.State) => {
  const response = await modelWithTools.invoke(state.messages);
  return { messages: [response] };
};

const toolNode = async (state: typeof AgentState.State) => {
  const lastMessage = state.messages.at(-1);
  if (!lastMessage || !AIMessage.isInstance(lastMessage)) {
    return { messages: [] };
  }

  const toolsByName = { [search.name]: search, [calculate.name]: calculate };
  const result = [];

  for (const toolCall of lastMessage.tool_calls ?? []) {
    const tool = toolsByName[toolCall.name];
    const observation = await tool.invoke(toolCall);
    result.push(observation);
  }

  return { messages: result };
};

const shouldContinue = (state: typeof AgentState.State) => {
  const lastMessage = state.messages.at(-1);
  if (lastMessage && AIMessage.isInstance(lastMessage) && lastMessage.tool_calls?.length) {
    return "tools";
  }
  return END;
};

// Dynamic agent: model decides when to stop
const agent = new StateGraph(AgentState)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue, ["tools", END])
  .addEdge("tools", "agent")
  .compile();
```
</typescript>
</ex-agent>

<ex-orchestrator>
<python>
Fan-out with Send API:

```python
from langgraph.types import Send
from typing import Annotated
import operator

class OrchestratorState(TypedDict):
    tasks: list[str]
    results: Annotated[list, operator.add]

def orchestrator(state: OrchestratorState):
    """Fan out tasks to workers."""
    return [
        Send("worker", {"task": task})
        for task in state["tasks"]
    ]

def worker(state: dict) -> dict:
    """Individual worker processes one task."""
    task = state["task"]
    result = f"Completed: {task}"
    return {"results": [result]}

def synthesize(state: OrchestratorState) -> dict:
    """Combine worker outputs."""
    summary = f"Processed {len(state['results'])} tasks"
    return {"summary": summary}

graph = (
    StateGraph(OrchestratorState)
    .add_node("worker", worker)
    .add_node("synthesize", synthesize)
    .add_conditional_edges(START, orchestrator, ["worker"])
    .add_edge("worker", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)

result = graph.invoke({
    "tasks": ["Task A", "Task B", "Task C"]
})
print(result["summary"])  # "Processed 3 tasks"
```
</python>

<typescript>
Fan-out with Send API:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const OrchestratorState = new StateSchema({
  tasks: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  summary: z.string().optional(),
});

const orchestrator = (state: typeof OrchestratorState.State) => {
  // Fan out tasks to workers
  return state.tasks.map(task => new Send("worker", { task }));
};

const worker = async (state: { task: string }) => {
  const result = `Completed: ${state.task}`;
  return { results: [result] };
};

const synthesize = async (state: typeof OrchestratorState.State) => {
  const summary = `Processed ${state.results.length} tasks`;
  return { summary };
};

const graph = new StateGraph(OrchestratorState)
  .addNode("worker", worker)
  .addNode("synthesize", synthesize)
  .addConditionalEdges(START, orchestrator, ["worker"])
  .addEdge("worker", "synthesize")
  .addEdge("synthesize", END)
  .compile();

const result = await graph.invoke({
  tasks: ["Task A", "Task B", "Task C"],
});
console.log(result.summary);  // "Processed 3 tasks"
```
</typescript>
</ex-orchestrator>

<ex-hybrid>
<python>
Mix deterministic and agentic steps:

```python
class HybridState(TypedDict):
    input: str
    validated: bool
    agent_response: str
    finalized: bool

def validate(state: HybridState) -> dict:
    """Fixed validation step."""
    return {"validated": True}

def agent_process(state: HybridState) -> dict:
    """Dynamic: agent decides how to process."""
    # Agent logic here
    response = f"Agent processed: {state['input']}"
    return {"agent_response": response}

def finalize(state: HybridState) -> dict:
    """Fixed finalization step."""
    return {"finalized": True}

# Hybrid: validate -> agent -> finalize
hybrid = (
    StateGraph(HybridState)
    .add_node("validate", validate)      # Workflow
    .add_node("agent", agent_process)    # Agent
    .add_node("finalize", finalize)      # Workflow
    .add_edge(START, "validate")
    .add_edge("validate", "agent")
    .add_edge("agent", "finalize")
    .add_edge("finalize", END)
    .compile()
)
```
</python>

<typescript>
Mix deterministic and agentic steps:

```typescript
import { StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const HybridState = new StateSchema({
  input: z.string(),
  validated: z.boolean(),
  agentResponse: z.string().optional(),
  finalized: z.boolean(),
});

const validate = async (state: typeof HybridState.State) => {
  return { validated: true };
};

const agentProcess = async (state: typeof HybridState.State) => {
  // Dynamic agent logic here
  const response = `Agent processed: ${state.input}`;
  return { agentResponse: response };
};

const finalize = async (state: typeof HybridState.State) => {
  return { finalized: true };
};

// Hybrid: validate -> agent -> finalize
const hybrid = new StateGraph(HybridState)
  .addNode("validate", validate)      // Workflow
  .addNode("agent", agentProcess)     // Agent
  .addNode("finalize", finalize)      // Workflow
  .addEdge(START, "validate")
  .addEdge("validate", "agent")
  .addEdge("agent", "finalize")
  .addEdge("finalize", END)
  .compile();
```
</typescript>
</ex-hybrid>

<ex-mapreduce>
<python>
Parallel processing with aggregation:

```python
class MapReduceState(TypedDict):
    documents: list[str]
    summaries: Annotated[list, operator.add]
    final_summary: str

def map_documents(state: MapReduceState):
    """Map: send each document to a worker."""
    return [
        Send("summarize", {"doc": doc})
        for doc in state["documents"]
    ]

def summarize(state: dict) -> dict:
    """Worker: summarize one document."""
    doc = state["doc"]
    summary = f"Summary of: {doc[:50]}..."
    return {"summaries": [summary]}

def reduce(state: MapReduceState) -> dict:
    """Reduce: combine all summaries."""
    final = " | ".join(state["summaries"])
    return {"final_summary": final}

graph = (
    StateGraph(MapReduceState)
    .add_node("summarize", summarize)
    .add_node("reduce", reduce)
    .add_conditional_edges(START, map_documents, ["summarize"])
    .add_edge("summarize", "reduce")
    .add_edge("reduce", END)
    .compile()
)

result = graph.invoke({
    "documents": ["Doc 1 content...", "Doc 2 content...", "Doc 3 content..."]
})
```
</python>

<typescript>
Parallel processing with aggregation:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const MapReduceState = new StateSchema({
  documents: z.array(z.string()),
  summaries: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  finalSummary: z.string().optional(),
});

const mapDocuments = (state: typeof MapReduceState.State) => {
  return state.documents.map(doc => new Send("summarize", { doc }));
};

const summarize = async (state: { doc: string }) => {
  const summary = `Summary of: ${state.doc.slice(0, 50)}...`;
  return { summaries: [summary] };
};

const reduce = async (state: typeof MapReduceState.State) => {
  const finalSummary = state.summaries.join(" | ");
  return { finalSummary };
};

const graph = new StateGraph(MapReduceState)
  .addNode("summarize", summarize)
  .addNode("reduce", reduce)
  .addConditionalEdges(START, mapDocuments, ["summarize"])
  .addEdge("summarize", "reduce")
  .addEdge("reduce", END)
  .compile();

const result = await graph.invoke({
  documents: ["Doc 1 content...", "Doc 2 content...", "Doc 3 content..."],
});
```
</typescript>
</ex-mapreduce>

<ex-router>
<python>
Route to multiple sources:

```python
from langgraph.types import Send

class RouterState(TypedDict):
    query: str
    sources: list[str]
    results: Annotated[list, operator.add]

def classify(state: RouterState) -> dict:
    """Determine which sources to query."""
    query = state["query"].lower()
    sources = []

    if "code" in query:
        sources.append("github")
    if "doc" in query:
        sources.append("notion")
    if "message" in query:
        sources.append("slack")

    return {"sources": sources}

def route_to_sources(state: RouterState):
    """Fan out to relevant sources."""
    return [
        Send(source, {"query": state["query"]})
        for source in state["sources"]
    ]

def query_github(state: dict) -> dict:
    return {"results": [f"GitHub: {state['query']}"]}

def query_notion(state: dict) -> dict:
    return {"results": [f"Notion: {state['query']}"]}

def query_slack(state: dict) -> dict:
    return {"results": [f"Slack: {state['query']}"]}

def synthesize(state: RouterState) -> dict:
    return {"final": " + ".join(state["results"])}

graph = (
    StateGraph(RouterState)
    .add_node("classify", classify)
    .add_node("github", query_github)
    .add_node("notion", query_notion)
    .add_node("slack", query_slack)
    .add_node("synthesize", synthesize)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_sources)
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)
```
</python>

<typescript>
Route to multiple sources:

```typescript
import { StateGraph, StateSchema, Send, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const RouterState = new StateSchema({
  query: z.string(),
  sources: z.array(z.string()),
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
  final: z.string().optional(),
});

const classify = async (state: typeof RouterState.State) => {
  const query = state.query.toLowerCase();
  const sources: string[] = [];

  if (query.includes("code")) sources.push("github");
  if (query.includes("doc")) sources.push("notion");
  if (query.includes("message")) sources.push("slack");

  return { sources };
};

const routeToSources = (state: typeof RouterState.State) => {
  return state.sources.map(source => new Send(source, { query: state.query }));
};

const queryGithub = async (state: { query: string }) => {
  return { results: [`GitHub: ${state.query}`] };
};

const queryNotion = async (state: { query: string }) => {
  return { results: [`Notion: ${state.query}`] };
};

const querySlack = async (state: { query: string }) => {
  return { results: [`Slack: ${state.query}`] };
};

const synthesize = async (state: typeof RouterState.State) => {
  return { final: state.results.join(" + ") };
};

const graph = new StateGraph(RouterState)
  .addNode("classify", classify)
  .addNode("github", queryGithub)
  .addNode("notion", queryNotion)
  .addNode("slack", querySlack)
  .addNode("synthesize", synthesize)
  .addEdge(START, "classify")
  .addConditionalEdges("classify", routeToSources, ["github", "notion", "slack"])
  .addEdge("github", "synthesize")
  .addEdge("notion", "synthesize")
  .addEdge("slack", "synthesize")
  .addEdge("synthesize", END)
  .compile();
```
</typescript>
</ex-router>

<boundaries>
**What You CAN Configure**

- Choose workflow vs agent pattern
- Mix deterministic and agentic steps
- Use Send API for parallel execution
- Define custom orchestrator logic
- Control worker node behavior
- Aggregate results with reducers

**What You CANNOT Configure**

- Change Send API message-passing model
- Bypass worker state isolation
- Modify parallel execution mechanism
- Override reducer behavior at runtime
</boundaries>

<fix-send-worker-state-isolation>
<python>
Workers receive isolated state:

```python
# WRONG - Workers share state, causing conflicts
class State(TypedDict):
    shared_counter: int  # All workers modify same counter!

# CORRECT - Each worker gets isolated input
def worker(state: dict) -> dict:
    # state is isolated to this worker
    return {"results": [process(state["task"])]}
```
</python>

<typescript>
Workers receive isolated state:

```typescript
// WRONG - Workers share state, causing conflicts
const State = new StateSchema({
  sharedCounter: z.number(),  // All workers modify same counter!
});

// CORRECT - Each worker gets isolated input
const worker = async (state: { task: string }) => {
  // state is isolated to this worker
  return { results: [process(state.task)] };
};
```
</typescript>
</fix-send-worker-state-isolation>

<fix-send-accumulator-reducer>
<python>
Use reducer to collect worker results:

```python
# WRONG - Last worker overwrites all others
class State(TypedDict):
    results: list  # No reducer!

# CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates
```
</python>

<typescript>
Use ReducedValue to collect results:

```typescript
// WRONG - Last worker overwrites all others
const State = new StateSchema({
  results: z.array(z.string()),  // No reducer!
});

// CORRECT - Use ReducedValue
import { ReducedValue } from "@langchain/langgraph";

const State = new StateSchema({
  results: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});
```
</typescript>
</fix-send-accumulator-reducer>

<fix-rigid-workflows>
<python>
Add error handling paths:

```python
# ANTI-PATTERN - Overly rigid workflow
# What if validation fails? No recovery path!
.add_edge("validate", "process")  # Always proceeds

# BETTER - Add conditional logic
def route_after_validate(state):
    if not state["validated"]:
        return "error_handler"
    return "process"

.add_conditional_edges("validate", route_after_validate)
```
</python>

<typescript>
Add error handling paths:

```typescript
// ANTI-PATTERN - Overly rigid workflow
.addEdge("validate", "process")  // Always proceeds, no error handling

// BETTER - Add conditional logic
const routeAfterValidate = (state) => {
  if (!state.validated) return "errorHandler";
  return "process";
};

.addConditionalEdges("validate", routeAfterValidate, ["process", "errorHandler"]);
```
</typescript>
</fix-rigid-workflows>

<fix-unpredictable-agents>
<python>
Add iteration limits as guardrails:

```python
# RISKY - Pure agent, no guardrails
# Agent might loop forever or make bad choices

# BETTER - Hybrid with constraints
def should_continue(state):
    # Add max iterations check
    if state["iterations"] > 10:
        return END
    if state["messages"][-1].tool_calls:
        return "tools"
    return END
```
</python>
</fix-unpredictable-agents>

<fix-await-async-nodes>
<typescript>
Await async invocations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" });
console.log(result.output);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" });
console.log(result.output);  // Works!
```
</typescript>
</fix-await-async-nodes>

<links>
**Python**
- [Workflows and Agents (Python)](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Send API Guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Map-Reduce Example](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)

**TypeScript**
- [Workflows and Agents (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/workflows-agents)
- [Send API Guide](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Map-Reduce Example](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
</links>
