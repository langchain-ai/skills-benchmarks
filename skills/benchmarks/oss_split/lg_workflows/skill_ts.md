---
name: LangGraph Workflows (TypeScript)
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

<ex-basic-workflow>
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

// Fixed workflow: validate → process
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
</ex-basic-workflow>

<ex-dynamic-agent>
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
  description: "Perform a mathematical operation",
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
</ex-dynamic-agent>

<ex-orchestrator-worker>
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
</ex-orchestrator-worker>

<ex-hybrid>
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

// Hybrid: validate → agent → finalize
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
</ex-hybrid>

<ex-map-reduce>
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
</ex-map-reduce>

<ex-parallel-router>
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
</ex-parallel-router>

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
</fix-send-worker-state-isolation>

<fix-send-accumulator-reducer>
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
</fix-send-accumulator-reducer>

<fix-rigid-workflows>
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
</fix-rigid-workflows>

<fix-await-async-nodes>
```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" });
console.log(result.output);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" });
console.log(result.output);  // Works!
```
</fix-await-async-nodes>

<documentation-links>
- [Workflows and Agents (JavaScript)](https://docs.langchain.com/oss/javascript/langgraph/workflows-agents)
- [Send API Guide](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Map-Reduce Example](https://docs.langchain.com/oss/javascript/langgraph/use-graph-api#map-reduce-and-the-send-api)
</documentation-links>
