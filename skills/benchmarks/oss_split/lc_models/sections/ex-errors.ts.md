Handle API errors:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

try {
  const response = await model.invoke("Hello!");
  console.log(response.content);
} catch (error) {
  if (error.status === 429) {
    console.error("Rate limit exceeded");
  } else if (error.status === 401) {
    console.error("Invalid API key");
  } else {
    console.error("Error:", error.message);
  }
}
```
