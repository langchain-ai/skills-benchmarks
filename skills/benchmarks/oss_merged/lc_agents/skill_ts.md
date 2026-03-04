---
name: langchain-agents-tools-js
description: "INVOKE THIS SKILL when building ANY LangChain/LangGraph agent with tools. Covers createAgent, tool(), Zod schemas, bindTools(), and tool message handling. CRITICAL: Fixes for missing tool descriptions, tool_call_id mismatches, and not checking for tool_calls."
---

<overview>
Agents combine language models with tools to create systems that can reason, act, and iterate.

**Key Components:**
- **tool()**: Create tools from functions with Zod schemas
- **bindTools()**: Attach tools to a model
- **Tool Calls**: Model requests in AIMessage.tool_calls
- **ToolMessage**: Results passed back to model
- **createAgent()**: Production-ready agent from langchain
</overview>

<agent-configuration-selection>

| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `createAgent({ model, tools })` | Search, calculator |
| Custom system instructions | Add `systemMessage` | Domain-specific behavior |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |

</agent-configuration-selection>

<tool-choice-strategies>

| Strategy | When to Use |
|----------|-------------|
| `"auto"` (default) | Model decides if/which tool |
| `"any"` | Force model to use at least one tool |
| `"tool_name"` | Force specific tool |

</tool-choice-strategies>

---

## Tool Definition

<ex-basic-tool>
Define a calculator tool using the tool() function with Zod schema validation.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const calculator = tool(
  async ({ operation, a, b }) => {
    const ops = { add: a + b, subtract: a - b, multiply: a * b, divide: a / b };
    return ops[operation];
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```
</ex-basic-tool>

<ex-tool-with-schema>
Define a tool with Zod schema for argument validation with default values.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchDatabase = tool(
  async ({ query, limit }) => `Found ${limit} results for: ${query}`,
  {
    name: "search_database",
    description: "Search the database for records",
    schema: z.object({
      query: z.string().describe("Search query"),
      limit: z.number().default(10).describe("Max results"),
    }),
  }
);
```
</ex-tool-with-schema>

---

## Agent Creation

<ex-basic-agent-with-tools>
Create a basic React agent with a search tool and invoke it with a user message.
```typescript
import { createAgent } from "langchain";
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => `Results for: ${query}`,
  { name: "search", description: "Search for information", schema: z.object({ query: z.string() }) }
);

const agent = createAgent({ model: "gpt-4.1", tools: [search] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for AI news" }]
});
console.log(result.messages.at(-1).content);
```
</ex-basic-agent-with-tools>

<ex-agent-with-persistence>
Create a React agent with MemorySaver checkpointer for conversation persistence across invokes.
```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [search],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);

const result = await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Response: "Your name is Alice"
```
</ex-agent-with-persistence>

---

## Tool Calling (Manual)

<ex-basic-tool-calling>
Bind a tool to a model and inspect the tool_calls returned by the model.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny, 72F`,
  { name: "get_weather", description: "Get weather", schema: z.object({ location: z.string() }) }
);

const model = new ChatOpenAI({ model: "gpt-4" });
const modelWithTools = model.bindTools([getWeather]);

const response = await modelWithTools.invoke("What's the weather in SF?");
console.log(response.tool_calls);
// [{ name: 'get_weather', args: { location: 'San Francisco' }, id: 'call_abc123' }]
```
</ex-basic-tool-calling>

<ex-executing-tool-calls>
Execute tool calls from the model response and pass results back for final answer.
```typescript
import { ToolMessage } from "@langchain/core/messages";

// Step 1: Model decides to call tool
const messages = [{ role: "user", content: "What's the weather in NYC?" }];
const response1 = await modelWithTools.invoke(messages);

// Step 2: Execute the tool
const toolResults = [];
for (const toolCall of response1.tool_calls ?? []) {
  const result = await getWeather.invoke(toolCall.args);
  toolResults.push(new ToolMessage({ content: result, tool_call_id: toolCall.id }));
}

// Step 3: Pass results back to model
messages.push(response1);
messages.push(...toolResults);

const response2 = await modelWithTools.invoke(messages);
console.log(response2.content);
```
</ex-executing-tool-calls>

<ex-parallel-tool-calling>
Models may return multiple tool_calls at once - iterate over all of them.
```typescript
const response = await modelWithTools.invoke("Get weather for NYC and news about AI");

// Model may call both tools in parallel
console.log(response.tool_calls);
// [
//   { name: 'get_weather', args: { location: 'NYC' }, id: 'call_1' },
//   { name: 'get_news', args: { topic: 'AI' }, id: 'call_2' }
// ]

// Execute ALL tool calls, not just the first one
for (const toolCall of response.tool_calls ?? []) {
  const result = await toolsByName[toolCall.name].invoke(toolCall.args);
}
```
</ex-parallel-tool-calling>

<boundaries>
### What You CAN Configure

- Model: Any chat model (OpenAI, Anthropic, etc.)
- Tools: Custom tools, built-in tools
- Checkpointer: Memory/persistence
- Tool choice strategy: auto, any, specific tool

### What You CANNOT Configure

- Tool execution order: Model decides
- Force model reasoning: Can't control how model decides
</boundaries>

<fix-tool-description>
Shows the difference between vague and clear tool descriptions for better model understanding.
```typescript
// WRONG: Vague description
const badTool = tool(
  async ({ data }) => "result",
  { name: "tool", description: "Does something", schema: z.object({ data: z.string() }) }
);

// CORRECT: Clear, specific descriptions
const goodTool = tool(
  async ({ query }) => "result",
  {
    name: "web_search",
    description: "Search the web for current information",
    schema: z.object({ query: z.string().describe("Search query (2-10 words)") }),
  }
);
```
</fix-tool-description>

<fix-forgetting-to-pass-tool-results-back>
Demonstrates the correct pattern of appending tool results to messages before re-invoking.
```typescript
// WRONG: Not passing tool results back
const response1 = await modelWithTools.invoke(messages);
const toolResult = await tool.invoke(response1.tool_calls[0].args);
// Missing: passing result back!

// CORRECT: Always pass results back
messages.push(response1);
messages.push(new ToolMessage({ content: toolResult, tool_call_id: response1.tool_calls[0].id }));
const response2 = await modelWithTools.invoke(messages);
```
</fix-forgetting-to-pass-tool-results-back>

<fix-tool-call-id-mismatch>
ToolMessage must have tool_call_id matching the original request.
```typescript
// WRONG: Hardcoded or wrong tool_call_id
const toolMessage = new ToolMessage({ content: "Sunny", tool_call_id: "wrong_id", name: "get_weather" });

// CORRECT: Use the ID from the tool call
const toolMessage = new ToolMessage({
  content: "Sunny",
  tool_call_id: response.tool_calls[0].id,  // Must match!
  name: "get_weather",
});

// OR let tool.invoke() handle it automatically
const toolMessage = await getWeather.invoke(response.tool_calls[0]);
```
</fix-tool-call-id-mismatch>

<fix-not-checking-for-tool-calls>
Always check if tool_calls exist before attempting to execute them.
```typescript
// WRONG: Assuming model always calls tools
const response = await modelWithTools.invoke("Hello");
await tool.invoke(response.tool_calls[0].args);  // Error if no tool calls!

// CORRECT: Check if tool calls exist
if (response.tool_calls?.length) {
  for (const toolCall of response.tool_calls) {
    await tool.invoke(toolCall.args);
  }
} else {
  console.log(response.content);
}
```
</fix-not-checking-for-tool-calls>

<fix-binding-tools-multiple-times>
Bind all tools in a single call instead of chaining bindTools which overwrites.
```typescript
// WRONG: Binding tools overwrites previous binding
const withTool1 = model.bindTools([tool1]);
const withTool2 = withTool1.bindTools([tool2]);  // Only has tool2!

// CORRECT: Bind all tools at once
const withBothTools = model.bindTools([tool1, tool2]);
```
</fix-binding-tools-multiple-times>

<fix-state-persistence>
Add a checkpointer and thread_id to enable conversation memory across invocations.
```typescript
// WRONG: No checkpointer - each invoke is isolated
const agent = createAgent({ model: "gpt-4.1", tools: [search] });
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember "Bob"

// CORRECT: Add checkpointer and thread_id
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({ model: "gpt-4.1", tools: [search], checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Bob"
```
</fix-state-persistence>
