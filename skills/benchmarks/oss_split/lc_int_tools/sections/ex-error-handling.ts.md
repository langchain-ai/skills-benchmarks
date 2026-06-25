Handle API errors gracefully in tools.

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
