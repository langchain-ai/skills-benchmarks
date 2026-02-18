---
name: LangChain Tools Integration (TypeScript)
description: [LangChain] Guide to using tool integrations in LangChain including pre-built toolkits, Tavily, Wikipedia, and custom tools
---

<overview>
Tools enable LLMs to interact with external systems, perform calculations, search the web, query databases, and more. They extend model capabilities beyond text generation, making agents truly actionable.

**Key Concepts:**
- **Tools**: Functions that agents can call to perform specific tasks
- **Tool Calling**: Models decide when and how to use tools based on user queries
- **Toolkits**: Collections of related tools
- **Tool Schema**: Describes tool parameters using Zod or JSON Schema
</overview>

<tool-selection-table>
| Tool/Toolkit | Best For | Package | Key Features |
|--------------|----------|---------|--------------|
| **Tavily Search** | Web search | `@langchain/community` | AI-optimized search API |
| **Wikipedia** | Encyclopedia queries | `@langchain/community` | Wikipedia API access |
| **Calculator** | Math operations | `@langchain/community` | Expression evaluation |
| **DuckDuckGo Search** | Privacy-focused search | `@langchain/community` | No API key needed |
| **Browser Tools** | Web automation | `@langchain/community` | Headless browsing |
| **Vector Store Tools** | Semantic search | Based on vector store | Query your data |
| **Custom Tools** | Your specific needs | `@langchain/core/tools` | Define any function |
</tool-selection-table>

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

<ex-tavily-search>
```typescript
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";

// Initialize Tavily (requires API key)
const searchTool = new TavilySearchResults({
  maxResults: 3,
  apiKey: process.env.TAVILY_API_KEY,
});

// Use directly
const results = await searchTool.invoke("Latest AI news");
console.log(results);

// Use with agent
import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const model = new ChatOpenAI({ modelName: "gpt-4" });
const agent = createReactAgent({
  llm: model,
  tools: [searchTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's new in AI today?" }]
});
```
</ex-tavily-search>

<ex-wikipedia>
```typescript
import { WikipediaQueryRun } from "@langchain/community/tools/wikipedia_query_run";

const wikipediaTool = new WikipediaQueryRun({
  topKResults: 3,
  maxDocContentLength: 4000,
});

// Query Wikipedia
const result = await wikipediaTool.invoke("Artificial Intelligence");
console.log(result);
```
</ex-wikipedia>

<ex-calculator>
```typescript
import { Calculator } from "@langchain/community/tools/calculator";

const calculator = new Calculator();

// Perform calculations
const result = await calculator.invoke("sqrt(144) + 5 * 3");
console.log(result); // "27"

// Use in agent for math problems
const mathAgent = createReactAgent({
  llm: model,
  tools: [calculator],
});
```
</ex-calculator>

<ex-duckduckgo>
```typescript
import { DuckDuckGoSearch } from "@langchain/community/tools/duckduckgo_search";

const searchTool = new DuckDuckGoSearch({
  maxResults: 5,
});

const results = await searchTool.invoke("LangChain framework");
```
</ex-duckduckgo>

<ex-custom-tool-zod>
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// Define custom tool
const weatherTool = tool(
  async ({ location, unit = "celsius" }) => {
    // Your implementation
    const data = await fetchWeather(location, unit);
    return `The weather in ${location} is ${data.temp}°${unit === "celsius" ? "C" : "F"}`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location. Use this when users ask about weather.",
    schema: z.object({
      location: z.string().describe("The city name, e.g., 'San Francisco'"),
      unit: z.enum(["celsius", "fahrenheit"]).optional().describe("Temperature unit"),
    }),
  }
);

// Use with agent
const agent = createReactAgent({
  llm: model,
  tools: [weatherTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in London?" }]
});
```
</ex-custom-tool-zod>

<ex-custom-tool-class>
```typescript
import { StructuredTool } from "@langchain/core/tools";
import { z } from "zod";

class DatabaseQueryTool extends StructuredTool {
  name = "database_query";
  description = "Query the customer database for information";

  schema = z.object({
    customerId: z.string().describe("Customer ID to look up"),
  });

  async _call({ customerId }: { customerId: string }): Promise<string> {
    // Your database logic
    const customer = await db.getCustomer(customerId);
    return JSON.stringify(customer);
  }
}

const dbTool = new DatabaseQueryTool();
```
</ex-custom-tool-class>

<ex-vector-store-tool>
```typescript
import { createRetrieverTool } from "langchain/tools/retriever";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

// Create vector store
const vectorStore = await MemoryVectorStore.fromTexts(
  ["LangChain is a framework...", "Agents use tools..."],
  [{}, {}],
  new OpenAIEmbeddings()
);

// Convert to tool
const retrieverTool = createRetrieverTool(
  vectorStore.asRetriever(),
  {
    name: "knowledge_base",
    description: "Search the knowledge base for information about LangChain",
  }
);

// Use in agent
const agent = createReactAgent({
  llm: model,
  tools: [retrieverTool],
});
```
</ex-vector-store-tool>

<ex-multiple-tools>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";
import { Calculator } from "@langchain/community/tools/calculator";
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

// Define tools
const searchTool = new TavilySearchResults({ maxResults: 3 });
const calculator = new Calculator();

const customTool = tool(
  async ({ query }) => {
    // Your custom logic
    return `Custom result for: ${query}`;
  },
  {
    name: "custom_lookup",
    description: "Look up custom information",
    schema: z.object({
      query: z.string().describe("The query to look up"),
    }),
  }
);

// Create agent with multiple tools
const agent = createReactAgent({
  llm: new ChatOpenAI({ modelName: "gpt-4" }),
  tools: [searchTool, calculator, customTool],
});

// Agent will choose appropriate tool(s)
const response = await agent.invoke({
  messages: [{
    role: "user",
    content: "Search for the population of Tokyo and calculate if it doubled"
  }]
});
```
</ex-multiple-tools>

<ex-error-handling>
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const apiTool = tool(
  async ({ endpoint }) => {
    try {
      const response = await fetch(`https://api.example.com/${endpoint}`);
      if (!response.ok) {
        return `API error: ${response.statusText}`;
      }
      const data = await response.json();
      return JSON.stringify(data);
    } catch (error) {
      return `Failed to call API: ${error.message}`;
    }
  },
  {
    name: "api_call",
    description: "Call external API",
    schema: z.object({
      endpoint: z.string().describe("API endpoint to call"),
    }),
  }
);
```
</ex-error-handling>

<boundaries>
**What Agents CAN Do**

* Use pre-built tools**
- Tavily search, Wikipedia, Calculator
- DuckDuckGo, web browsers
- Any tool from LangChain community

* Create custom tools**
- Define functions with Zod schemas
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

**What Agents CANNOT Do**

* Execute arbitrary code safely**
- Cannot run untrusted code
- Need sandboxing for code execution

* Bypass authentication**
- Tools need proper API keys
- Cannot access protected resources without credentials

* Guarantee tool selection**
- Model decides which tool to use
- Cannot force specific tool usage (without prompting)

* Use tools model doesn't support**
- Not all models support tool calling
- Need GPT-4, Claude 3, or similar
</boundaries>

<fix-api-keys-required>
```typescript
// WRONG: Missing API key
const tool = new TavilySearchResults();
await tool.invoke("query"); // Error!

// CORRECT: Provide API key
const tool = new TavilySearchResults({
  apiKey: process.env.TAVILY_API_KEY,
});
```
</fix-api-keys-required>

<fix-model-must-support-tools>
```typescript
// WRONG: Model doesn't support tool calling
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This model doesn't support tools!

// CORRECT: Use tool-capable model
const model = new ChatOpenAI({ modelName: "gpt-4" });
const modelWithTools = model.bindTools([myTool]);
```
</fix-model-must-support-tools>

<fix-tool-description-matters>
```typescript
// WRONG: Poor description
const tool = tool(
  async ({ x }) => x * 2,
  {
    name: "tool1",
    description: "A tool", // Too vague!
    schema: z.object({ x: z.number() }),
  }
);

// CORRECT: Clear, specific description
const tool = tool(
  async ({ number }) => number * 2,
  {
    name: "double_number",
    description: "Multiply a number by 2. Use this when the user wants to double a value.",
    schema: z.object({
      number: z.number().describe("The number to double"),
    }),
  }
);
```
</fix-tool-description-matters>

<fix-schema-validation>
```typescript
// WRONG: No schema validation
const tool = tool(
  async ({ location }) => {
    // Assumes location is a string, but no validation
    return location.toUpperCase(); // Could crash!
  },
  {
    name: "format_location",
    description: "Format location",
    schema: z.object({ location: z.any() }), // Too permissive
  }
);

// CORRECT: Proper schema
const tool = tool(
  async ({ location }) => {
    return location.toUpperCase();
  },
  {
    name: "format_location",
    description: "Format location name to uppercase",
    schema: z.object({
      location: z.string().describe("Location name"),
    }),
  }
);
```
</fix-schema-validation>

<documentation-links>
- [LangChain JS Tools](https://js.langchain.com/docs/integrations/tools/)
- [Custom Tools Guide](https://js.langchain.com/docs/how_to/custom_tools/)
- [Tavily](https://docs.tavily.com/)
</documentation-links>

<package-installation>
```bash
# Community tools
npm install @langchain/community

# Core tools
npm install @langchain/core

# Specific integrations
npm install @langchain/openai  # For OpenAI-based tools
```
</package-installation>
