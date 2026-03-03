---
name: langchain-tool-calling-js
description: "[LangChain] How chat models call tools - includes bind_tools, tool choice strategies, parallel tool calling, and tool message handling"
---

<overview>
Tool calling allows chat models to request execution of external functions. Models decide which tools to call based on user input, and the results are passed back to the model for further reasoning. This is the foundation of agentic behavior.

**Key Concepts:**
- **bindTools()**: Attach tools to a model
- **Tool Calls**: Model requests to execute tools (in AIMessage.tool_calls)
- **Tool Messages**: Results passed back to model (ToolMessage)
- **Tool Choice**: Control which tools the model can use
</overview>

<when-to-use>

| Scenario | Use Tool Calling? | Why |
|----------|------------------|-----|
| Need external data (API, database) | Yes | Model can't access external data directly |
| Multi-step reasoning with actions | Yes | Model decides next action based on results |
| Simple Q&A | No | No tools needed |
| Predetermined workflow | Partial Maybe | Consider if model needs to decide steps |

</when-to-use>

<tool-choice-strategies>

| Strategy | When to Use | Example |
|----------|-------------|---------|
| `"auto"` (default) | Model decides if/which tool to use | General purpose |
| `"any"` | Force model to use at least one tool | Extraction, classification |
| `"tool_name"` | Force specific tool | When you know which tool is needed |
| `"none"` | Prevent tool use | After tools are executed |

</tool-choice-strategies>

<handling-tool-calls-patterns>

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Manual execution | Outside of agents | Testing, custom workflows |
| Agent loop | Production use | createAgent handles automatically |
| Parallel execution | Multiple independent tools | Weather + news queries |

</handling-tool-calls-patterns>

<ex-basic>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { z } from "zod";

// Define a tool
const getWeather = tool(
  async ({ location }: { location: string }) => {
    return `Weather in ${location}: Sunny, 72°F`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location",
    schema: z.object({
      location: z.string().describe("City name"),
    }),
  }
);

// Bind tool to model
const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getWeather]);

// Model will decide to call the tool
const response = await modelWithTools.invoke(
  "What's the weather in San Francisco?"
);

// Check if model called a tool
console.log(response.tool_calls);
// [{
//   name: "get_weather",
//   args: { location: "San Francisco" },
//   id: "call_abc123"
// }]
```
</ex-basic>

<ex-manual-execution>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { ToolMessage } from "langchain";

const getTool = tool(
  async ({ location }) => `Weather in ${location}: Sunny`,
  {
    name: "get_weather",
    description: "Get weather",
    schema: z.object({ location: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getTool]);

// Step 1: Model decides to call tool
const messages = [{ role: "user", content: "What's the weather in NYC?" }];
const response1 = await modelWithTools.invoke(messages);

// Step 2: Execute the tool
const toolResults = [];
for (const toolCall of response1.tool_calls || []) {
  const result = await getTool.invoke(toolCall);
  toolResults.push(result); // This is a ToolMessage
}

// Step 3: Pass results back to model
messages.push(response1); // Add AI message with tool calls
messages.push(...toolResults); // Add tool results

const response2 = await modelWithTools.invoke(messages);
console.log(response2.content); // Final answer using tool results
```
</ex-manual-execution>

<ex-force-tool>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const extractInfo = tool(
  async ({ name, email }) => ({ name, email }),
  {
    name: "extract_info",
    description: "Extract name and email",
    schema: z.object({
      name: z.string(),
      email: z.string(),
    }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });

// Force model to use this specific tool
const modelWithTools = model.bindTools([extractInfo], {
  tool_choice: "extract_info", // Must use this tool
});

const response = await modelWithTools.invoke(
  "Contact: John Doe (john@example.com)"
);

// Model always calls extract_info
console.log(response.tool_calls[0].args);
// { name: "John Doe", email: "john@example.com" }
```
</ex-force-tool>

<ex-force-any>
```typescript
// Force model to use at least one tool (any of them)
const modelWithTools = model.bindTools(
  [tool1, tool2, tool3],
  { tool_choice: "any" }
);

// Model must call at least one tool, can't respond with just text
const response = await modelWithTools.invoke("Process this data");
```
</ex-force-any>

<ex-parallel>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny`,
  {
    name: "get_weather",
    description: "Get weather",
    schema: z.object({ location: z.string() }),
  }
);

const getNews = tool(
  async ({ topic }) => `Latest news about ${topic}`,
  {
    name: "get_news",
    description: "Get news",
    schema: z.object({ topic: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getWeather, getNews]);

const response = await modelWithTools.invoke(
  "Get weather for NYC and news about AI"
);

// Model may call both tools in parallel
console.log(response.tool_calls);
// [
//   { name: "get_weather", args: { location: "NYC" }, id: "call_1" },
//   { name: "get_news", args: { topic: "AI" }, id: "call_2" }
// ]
```
</ex-parallel>

<ex-tool-message>
```typescript
import { ToolMessage } from "langchain";

// Tool messages link back to the tool call that requested them
const toolMessage = new ToolMessage({
  content: "Weather in Paris: Sunny, 72°F",
  tool_call_id: "call_abc123", // Must match AIMessage tool_call id
  name: "get_weather", // Tool name
});

// Or created automatically by tool.invoke()
const result = await getTool.invoke({
  name: "get_weather",
  args: { location: "Paris" },
  id: "call_abc123",
});
// result is a ToolMessage with proper structure
```
</ex-tool-message>

<ex-error-handling>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { ToolMessage } from "langchain";

const riskyTool = tool(
  async ({ data }) => {
    if (!data) throw new Error("Missing data");
    return "Success";
  },
  {
    name: "risky_tool",
    description: "A tool that might fail",
    schema: z.object({ data: z.string().optional() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([riskyTool]);

const response = await modelWithTools.invoke("Process this");

// Execute tools with error handling
const toolResults = [];
for (const toolCall of response.tool_calls || []) {
  try {
    const result = await riskyTool.invoke(toolCall);
    toolResults.push(result);
  } catch (error) {
    // Return error as tool message
    toolResults.push(
      new ToolMessage({
        content: `Error: ${error.message}`,
        tool_call_id: toolCall.id,
        name: toolCall.name,
      })
    );
  }
}
```
</ex-error-handling>

<ex-builtin-tools>
```typescript
import { ChatOpenAI } from "@langchain/openai";

// OpenAI has built-in tools
const model = new ChatOpenAI({
  model: "gpt-4.1",
  // Enable code interpreter
  tools: [{ type: "code_interpreter" }],
});

// Anthropic has built-in tools
import { ChatAnthropic } from "@langchain/anthropic";

const claude = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  // These are provider parameters, not bindTools()
});
```
</ex-builtin-tools>

<ex-conditional-binding>
```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

function getModelWithTools(userRole: string) {
  const tools = [publicTool];

  if (userRole === "admin") {
    tools.push(adminTool);
  }

  return model.bindTools(tools);
}

// Different users get different tools
const adminModel = getModelWithTools("admin");
const userModel = getModelWithTools("user");
```
</ex-conditional-binding>

<ex-conversation>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const searchTool = tool(
  async ({ query }) => `Results for: ${query}`,
  {
    name: "search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([searchTool]);

const messages = [
  { role: "user", content: "Search for LangChain" },
];

// First call: model decides to use tool
const response1 = await modelWithTools.invoke(messages);
messages.push(response1);

// Execute tools
for (const toolCall of response1.tool_calls || []) {
  const result = await searchTool.invoke(toolCall);
  messages.push(result);
}

// Second call: model uses tool results
const response2 = await modelWithTools.invoke(messages);
console.log(response2.content); // Answer based on search results

// Continue conversation
messages.push(response2);
messages.push({ role: "user", content: "Tell me more" });

const response3 = await modelWithTools.invoke(messages);
// Model can call tools again if needed
```
</ex-conversation>

<boundaries>
**What You CAN Configure**

* Which tools are available**: bindTools([tool1, tool2])
* Tool choice strategy**: auto, any, specific tool, none
* Tool execution logic**: Custom error handling, retries
* Tool parameters**: Via tool schema
* Multiple tool calls**: Models can call multiple tools

**What You CANNOT Configure**

* Force model reasoning**: Can't control how model decides
* Tool call order**: Model decides (can call in parallel)
* Prevent all tool calls**: Use tool_choice or don't bind tools
* Modify tool call after model generates**: Tool calls are immutable
</boundaries>

<fix-forgetting-tool-results>
```typescript
// Problem: Not passing tool results back to model
const response1 = await modelWithTools.invoke(messages);
const toolResult = await tool.invoke(response1.tool_calls[0]);
// Missing: passing result back to model!

// Solution: Always pass results back
messages.push(response1); // AI message with tool calls
messages.push(toolResult); // Tool result
const response2 = await modelWithTools.invoke(messages);
```
</fix-forgetting-tool-results>

<fix-tool-call-id-mismatch>
```typescript
// Problem: Wrong tool_call_id
const response = await modelWithTools.invoke("Get weather");
const toolMessage = new ToolMessage({
  content: "Sunny",
  tool_call_id: "wrong_id", // Doesn't match!
  name: "get_weather",
});

// Solution: Use correct ID from tool call
const toolMessage = new ToolMessage({
  content: "Sunny",
  tool_call_id: response.tool_calls[0].id, // Correct ID
  name: "get_weather",
});

// OR use tool.invoke() which handles this automatically
const toolMessage = await getTool.invoke(response.tool_calls[0]);
```
</fix-tool-call-id-mismatch>

<fix-not-checking-for-tool-calls>
```typescript
// Problem: Assuming model always calls tools
const response = await modelWithTools.invoke("Hello");
await tool.invoke(response.tool_calls[0]); // Error if no tool calls!

// Solution: Check if tool calls exist
if (response.tool_calls && response.tool_calls.length > 0) {
  for (const toolCall of response.tool_calls) {
    await tool.invoke(toolCall);
  }
} else {
  // Model responded without calling tools
  console.log(response.content);
}
```
</fix-not-checking-for-tool-calls>

<fix-binding-tools-multiple-times>
```typescript
// Problem: Binding tools overwrites previous binding
const model = new ChatOpenAI({ model: "gpt-4.1" });
const withTool1 = model.bindTools([tool1]);
const withTool2 = withTool1.bindTools([tool2]); // Only has tool2!

// Solution: Bind all tools at once
const withBothTools = model.bindTools([tool1, tool2]);
```
</fix-binding-tools-multiple-times>

<fix-async-tool-execution>
```typescript
// Problem: Not awaiting async tool
const toolResults = response.tool_calls.map(async (tc) => {
  return await tool.invoke(tc); // Returns Promise!
});
messages.push(...toolResults); // Pushing Promises, not results!

// Solution: Use Promise.all or for...of
const toolResults = await Promise.all(
  response.tool_calls.map(tc => tool.invoke(tc))
);
messages.push(...toolResults);

// Or with for...of
const toolResults = [];
for (const toolCall of response.tool_calls) {
  const result = await tool.invoke(toolCall);
  toolResults.push(result);
}
```
</fix-async-tool-execution>

<fix-tool-choice-confusion>
```typescript
// Problem: Using wrong tool choice syntax
const model = new ChatOpenAI({ model: "gpt-4.1" });
model.bindTools([tool], "required"); // Wrong!

// Solution: Use correct option format
model.bindTools([tool], { tool_choice: "any" }); // Force any tool
model.bindTools([tool], { tool_choice: "tool_name" }); // Force specific
model.bindTools([tool]); // tool_choice: "auto" (default)
```
</fix-tool-choice-confusion>

<documentation-links>
- [Tool Calling Overview](https://docs.langchain.com/oss/javascript/langchain/models)
- [Tool Calls in Messages](https://docs.langchain.com/oss/javascript/langchain/messages)
- [Tools Guide](https://docs.langchain.com/oss/javascript/langchain/tools)
- [OpenAI Tool Calling](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
</documentation-links>
