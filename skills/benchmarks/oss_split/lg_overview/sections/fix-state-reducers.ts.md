Use MessagesValue for message handling:

```typescript
// WRONG - Messages will be overwritten, not appended
const BadState = new StateSchema({
  messages: z.array(BaseMessageSchema),  // No reducer!
});

// CORRECT - Use MessagesValue for automatic message handling
import { MessagesValue } from "@langchain/langgraph";

const GoodState = new StateSchema({
  messages: MessagesValue,  // Handles message updates correctly
});
```
