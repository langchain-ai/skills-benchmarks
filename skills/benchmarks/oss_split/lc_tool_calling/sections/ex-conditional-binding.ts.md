Bind different tools based on user role.

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
