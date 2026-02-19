---
name: LangChain Tools (TypeScript)
description: "[LangChain] Define and use tools in LangChain - includes @tool decorator, custom tools, built-in tools, and tool schemas"
---

<overview>
Tools are functions that agents can execute to perform actions like fetching data, running code, or querying databases. Tools have schemas that describe their purpose and parameters, helping models understand when and how to use them.

**Key Concepts:**
- **tool()**: Decorator to create tools from functions
- **Schema**: Zod schema defining tool parameters
- **Description**: Helps model understand when to use the tool
- **Built-in Tools**: Pre-made tools for common tasks
</overview>

<when-to-define-custom-tools>
| Scenario | Create Custom Tool? | Why |
|----------|---------------------|-----|
| Domain-specific logic | Yes | Unique to your application |
| Third-party API integration | Yes | Custom integration needed |
| Database queries | Yes | Your schema/data |
| Common utilities (search, calc) | Partial Maybe | Check for existing tools first |
| File operations | Partial Maybe | Built-in filesystem tools exist |
</when-to-define-custom-tools>

<tool-definition-methods>
| Method | When to Use | Example |
|--------|-------------|---------|
| `tool()` with function | Simple tools | Basic transformations |
| `tool()` with schema | Complex parameters | Multiple typed fields |
| `StructuredTool` | Full control | Custom error handling |
| Built-in tools | Common operations | Search, code execution |
</tool-definition-methods>

<ex-basic-tool-definition>
```typescript
import { tool } from "langchain";
import { z } from "zod";

// Simple tool
const calculator = tool(
  async ({ operation, a, b }: { operation: string; a: number; b: number }) => {
    if (operation === "add") return a + b;
    if (operation === "multiply") return a * b;
    throw new Error(`Unknown operation: ${operation}`);
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations. Use this when you need to compute numbers.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]).describe("The mathematical operation"),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);

// Use with agent
const result = await calculator.invoke({
  operation: "add",
  a: 5,
  b: 3,
});
console.log(result); // "8"
```
</ex-basic-tool-definition>

<ex-tool-with-detailed-schema>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const searchDatabase = tool(
  async ({ query, limit, filters }) => {
    // Your database search logic
    return `Found ${limit} results for: ${query}`;
  },
  {
    name: "search_database",
    description: "Search the customer database for records matching criteria",
    schema: z.object({
      query: z.string().describe("Search query (keywords or customer name)"),
      limit: z.number().default(10).describe("Maximum number of results to return"),
      filters: z.object({
        status: z.enum(["active", "inactive", "pending"]).optional(),
        created_after: z.string().optional().describe("ISO date string"),
      }).optional(),
    }),
  }
);
```
</ex-tool-with-detailed-schema>

<ex-async-tool>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const fetchWeather = tool(
  async ({ location }: { location: string }) => {
    // Async API call
    const response = await fetch(
      `https://api.weather.com/v1/location/${location}`
    );
    const data = await response.json();
    return `Temperature: ${data.temp}°F, Conditions: ${data.conditions}`;
  },
  {
    name: "get_weather",
    description: "Get current weather conditions for a location",
    schema: z.object({
      location: z.string().describe("City name or ZIP code"),
    }),
  }
);
```
</ex-async-tool>

<ex-tool-with-error-handling>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const divisionTool = tool(
  async ({ numerator, denominator }) => {
    if (denominator === 0) {
      throw new Error("Cannot divide by zero");
    }
    return numerator / denominator;
  },
  {
    name: "divide",
    description: "Divide two numbers",
    schema: z.object({
      numerator: z.number(),
      denominator: z.number(),
    }),
  }
);

// Error will be caught and returned as ToolMessage
```
</ex-tool-with-error-handling>

<ex-tool-with-side-effects>
```typescript
import { tool } from "langchain";
import { z } from "zod";
import fs from "fs/promises";

const writeFile = tool(
  async ({ filepath, content }) => {
    await fs.writeFile(filepath, content, "utf-8");
    return `Successfully wrote ${content.length} characters to ${filepath}`;
  },
  {
    name: "write_file",
    description: "Write content to a file. Use carefully as this modifies the filesystem.",
    schema: z.object({
      filepath: z.string().describe("Path to the file"),
      content: z.string().describe("Content to write"),
    }),
  }
);
```
</ex-tool-with-side-effects>

<ex-tool-with-external-dependencies>
```typescript
import { tool } from "langchain";
import { z } from "zod";
import axios from "axios";

const githubSearch = tool(
  async ({ query, language }) => {
    const response = await axios.get(
      "https://api.github.com/search/repositories",
      {
        params: { q: `${query} language:${language}`, sort: "stars" },
        headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
      }
    );

    const repos = response.data.items.slice(0, 5);
    return repos.map(r => `${r.full_name} (stars: ${r.stargazers_count})`).join("\n");
  },
  {
    name: "search_github",
    description: "Search GitHub repositories",
    schema: z.object({
      query: z.string().describe("Search query"),
      language: z.string().optional().describe("Programming language filter"),
    }),
  }
);
```
</ex-tool-with-external-dependencies>

<ex-tool-with-complex-return-type>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const analyzeText = tool(
  async ({ text }) => {
    return JSON.stringify({
      word_count: text.split(/\s+/).length,
      char_count: text.length,
      sentences: text.split(/[.!?]+/).length,
      avg_word_length: text.split(/\s+/).reduce((sum, w) => sum + w.length, 0) / text.split(/\s+/).length,
    });
  },
  {
    name: "analyze_text",
    description: "Analyze text statistics",
    schema: z.object({
      text: z.string().describe("Text to analyze"),
    }),
  }
);
```
</ex-tool-with-complex-return-type>

<ex-tool-with-runtime-configuration>
```typescript
import { tool } from "langchain";
import { z } from "zod";

function createDatabaseTool(connectionString: string) {
  return tool(
    async ({ query }) => {
      // Use connectionString to connect to DB
      const results = await db.query(query);
      return JSON.stringify(results);
    },
    {
      name: "query_database",
      description: "Execute SQL query on the database",
      schema: z.object({
        query: z.string().describe("SQL query to execute"),
      }),
    }
  );
}

// Create tool with specific configuration
const prodDbTool = createDatabaseTool(process.env.PROD_DB_URL);
const devDbTool = createDatabaseTool(process.env.DEV_DB_URL);
```
</ex-tool-with-runtime-configuration>

<ex-multiple-related-tools>
```typescript
import { tool } from "langchain";
import { z } from "zod";

// Toolkit pattern: group of related tools
const emailTools = {
  send: tool(
    async ({ to, subject, body }) => {
      // Send email logic
      return `Email sent to ${to}`;
    },
    {
      name: "send_email",
      description: "Send an email message",
      schema: z.object({
        to: z.string().email(),
        subject: z.string(),
        body: z.string(),
      }),
    }
  ),

  read: tool(
    async ({ folder, limit }) => {
      // Read emails logic
      return `Retrieved ${limit} emails from ${folder}`;
    },
    {
      name: "read_emails",
      description: "Read emails from a folder",
      schema: z.object({
        folder: z.string().default("inbox"),
        limit: z.number().default(10),
      }),
    }
  ),
};

// Use all email tools
const agent = createAgent({
  model: "gpt-4.1",
  tools: Object.values(emailTools),
});
```
</ex-multiple-related-tools>

<ex-tool-with-response-format-validation>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const getUser = tool(
  async ({ userId }) => {
    const user = await db.users.findById(userId);

    // Return structured data as JSON string
    return JSON.stringify({
      id: user.id,
      name: user.name,
      email: user.email,
      created: user.createdAt.toISOString(),
    });
  },
  {
    name: "get_user",
    description: "Get user information by ID",
    schema: z.object({
      userId: z.string().describe("User ID to lookup"),
    }),
  }
);
```
</ex-tool-with-response-format-validation>

<ex-tool-with-streaming-updates>
```typescript
import { tool } from "langchain";
import { z } from "zod";

const processLargeFile = tool(
  async ({ filepath }, { runtime }) => {
    const totalLines = 1000;

    for (let i = 0; i < totalLines; i += 100) {
      // Stream progress updates
      await runtime.stream_writer.write({
        type: "progress",
        data: { processed: i, total: totalLines },
      });

      // Process chunk
      await processChunk(i, i + 100);
    }

    return "Processing complete";
  },
  {
    name: "process_file",
    description: "Process a large file with progress updates",
    schema: z.object({
      filepath: z.string(),
    }),
  }
);
```
</ex-tool-with-streaming-updates>

<boundaries>
**What You CAN Configure:**
- Function logic: Any JavaScript/TypeScript code
- Parameters: Via Zod schema with descriptions
- Name and description: Guide model's tool selection
- Return value: Any serializable data (string, JSON, etc.)
- Async operations: Tools can be async
- Error handling: Throw errors or return error messages

**What You CANNOT Configure:**
- When model calls tool: Model decides based on context
- Tool call order: Model determines execution flow
- Parameter values: Model generates based on schema
- Response format from model: Tool returns, model interprets
</boundaries>

<fix-poor-tool-descriptions>
```typescript
// WRONG: Problem: Vague description
const badTool = tool(
  async ({ data }) => "result",
  {
    name: "tool",
    description: "Does something with data", // Too vague!
    schema: z.object({ data: z.string() }),
  }
);

// CORRECT: Solution: Specific, actionable description
const goodTool = tool(
  async ({ query }) => searchDatabase(query),
  {
    name: "search_customers",
    description: "Search customer database by name, email, or ID. Returns customer records with contact information. Use this when user asks about customer data.",
    schema: z.object({
      query: z.string().describe("Customer name, email, or ID to search for"),
    }),
  }
);
```
</fix-poor-tool-descriptions>

<fix-missing-parameter-descriptions>
```typescript
// WRONG: Problem: No field descriptions
const badSchema = z.object({
  query: z.string(),
  limit: z.number(),
});

// CORRECT: Solution: Describe each field
const goodSchema = z.object({
  query: z.string().describe("Search terms or keywords"),
  limit: z.number().describe("Maximum results to return (1-100)"),
});
```
</fix-missing-parameter-descriptions>

<fix-non-serializable-return-values>
```typescript
// WRONG: Problem: Returning complex objects
const badTool = tool(
  async () => new Date(), // Date not serializable!
  { name: "get_time", description: "Get time", schema: z.object({}) }
);

// CORRECT: Solution: Return strings or JSON
const goodTool = tool(
  async () => new Date().toISOString(),
  { name: "get_time", description: "Get current time", schema: z.object({}) }
);

// Or stringify objects
const dataTool = tool(
  async () => JSON.stringify({ timestamp: Date.now(), user: getCurrentUser() }),
  { name: "get_data", description: "Get data", schema: z.object({}) }
);
```
</fix-non-serializable-return-values>

<fix-tools-without-schemas>
```typescript
// WRONG: Problem: No schema
const badTool = tool(
  async (input: any) => "result",
  { name: "tool", description: "A tool" }
  // Missing schema!
);

// CORRECT: Solution: Always provide schema
const goodTool = tool(
  async ({ input }) => "result",
  {
    name: "tool",
    description: "A tool",
    schema: z.object({ input: z.string() }), // Clear schema
  }
);
```
</fix-tools-without-schemas>

<fix-forgetting-async>
```typescript
// WRONG: Problem: Not awaiting async operations
const badTool = tool(
  ({ url }) => {
    fetch(url); // Not awaited!
    return "done";
  },
  {
    name: "fetch_url",
    description: "Fetch URL",
    schema: z.object({ url: z.string() }),
  }
);

// CORRECT: Solution: Use async/await
const goodTool = tool(
  async ({ url }) => {
    const response = await fetch(url);
    const data = await response.text();
    return data;
  },
  {
    name: "fetch_url",
    description: "Fetch URL content",
    schema: z.object({ url: z.string().url() }),
  }
);
```
</fix-forgetting-async>

<fix-tool-names-with-spaces-or-special-chars>
```typescript
// WRONG: Problem: Invalid tool name
const badTool = tool(
  async () => "result",
  {
    name: "Get Weather!", // Special chars not allowed
    description: "Get weather",
    schema: z.object({}),
  }
);

// CORRECT: Solution: Use snake_case or camelCase
const goodTool = tool(
  async () => "result",
  {
    name: "get_weather", // Valid name
    description: "Get weather",
    schema: z.object({}),
  }
);
```
</fix-tool-names-with-spaces-or-special-chars>

<documentation-links>
- [Tools Overview](https://docs.langchain.com/oss/javascript/langchain/tools)
- [Tool Integrations](https://docs.langchain.com/oss/javascript/integrations/tools/index)
- [Custom Tools Guide](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
</documentation-links>
