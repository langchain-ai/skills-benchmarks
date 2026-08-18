Add safety checks before deployment:

```typescript
import { createAgent, todoListMiddleware } from "langchain";
import { tool } from "langchain";
import { z } from "zod";

const runTests = tool(
  async ({ testSuite }: { testSuite: string }) => {
    return `Tests in ${testSuite} passed`;
  },
  {
    name: "run_tests",
    description: "Run a test suite",
    schema: z.object({ testSuite: z.string() }),
  }
);

const deployCode = tool(
  async ({ environment }: { environment: string }) => {
    return `Deployed to ${environment}`;
  },
  {
    name: "deploy_code",
    description: "Deploy code to an environment",
    schema: z.object({ environment: z.string() }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [runTests, deployCode],
  middleware: [
    todoListMiddleware({
      systemPrompt: `For deployment tasks, always:
      1. Create a todo list with safety checks
      2. Run tests before deployment
      3. Mark each step as completed before proceeding
      `,
    }),
  ],
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Deploy the application to production"
  }]
});
```
