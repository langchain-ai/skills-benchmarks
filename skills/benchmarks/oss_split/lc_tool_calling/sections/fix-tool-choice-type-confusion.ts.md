Use correct option format for tool_choice.

```typescript
// Problem: Using wrong tool choice syntax
const model = new ChatOpenAI({ model: "gpt-4.1" });
model.bindTools([tool], "required"); // Wrong!

// Solution: Use correct option format
model.bindTools([tool], { tool_choice: "any" }); // Force any tool
model.bindTools([tool], { tool_choice: "tool_name" }); // Force specific
model.bindTools([tool]); // tool_choice: "auto" (default)
```
