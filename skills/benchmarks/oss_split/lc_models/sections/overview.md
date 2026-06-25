Chat models are the core of LangChain applications. They take messages as input and return AI-generated messages as output. LangChain provides a unified interface across multiple providers (OpenAI, Anthropic, Google, etc.).

Key Concepts:
- **init_chat_model() / initChatModel()**: Universal initialization for any provider
- **Provider-specific classes**: Direct initialization (ChatOpenAI, ChatAnthropic, etc.)
- **Messages**: Structured input/output format (HumanMessage, AIMessage, etc.)
- **Invocation patterns**: invoke(), stream(), batch()
