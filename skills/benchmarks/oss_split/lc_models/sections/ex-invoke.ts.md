Basic invoke with string and messages:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// String input (converted to HumanMessage)
const response = await model.invoke("What is LangChain?");
console.log(response.content);

// Message array input
const response2 = await model.invoke([
  { role: "user", content: "Hello!" }
]);
console.log(response2.content);
```
