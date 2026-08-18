| Method | When to Use | Python Example | TypeScript Example |
|--------|-------------|----------------|-------------------|
| Universal init | Quick switching between providers | `init_chat_model("openai:gpt-4.1")` | `initChatModel("openai:gpt-4.1")` |
| Provider class | Need provider-specific features | `ChatOpenAI(model="gpt-4.1")` | `new ChatOpenAI({ model: "gpt-4.1" })` |
| With configuration | Custom parameters needed | Temperature, max tokens, etc. | Temperature, max tokens, etc. |
