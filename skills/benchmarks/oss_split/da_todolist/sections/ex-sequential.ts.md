Create todos upfront for multi-step task:

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: `Create a REST API for a todo application:
    1. Design the data models
    2. Implement CRUD endpoints
    3. Add authentication
    4. Write tests
    5. Create API documentation
    `
  }]
});

// Agent's internal planning (via write_todos):
// [
//   { content: "Design data models for Todo items", status: "pending" },
//   { content: "Implement CRUD endpoints (GET, POST, PUT, DELETE)", status: "pending" },
//   { content: "Add JWT authentication middleware", status: "pending" },
//   { content: "Write unit and integration tests", status: "pending" },
//   { content: "Generate OpenAPI documentation", status: "pending" }
// ]
```
