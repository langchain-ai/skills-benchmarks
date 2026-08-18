What You CAN Do:
- **Use pre-built tools** - Tavily search, Wikipedia, DuckDuckGo, ArXiv, calculators, web browsers, any tool from LangChain community
- **Create custom tools** - Define functions with @tool decorator (Python) or tool() (TypeScript), implement class-based tools, convert retrievers to tools
- **Combine multiple tools** - Give agents access to many tools, let models choose appropriate tools, chain tool calls
- **Handle tool responses** - Parse tool output, use results in conversation, error handling

What You CANNOT Do:
- **Execute arbitrary code safely** - Cannot run untrusted code; need sandboxing for code execution
- **Bypass authentication** - Tools need proper API keys; cannot access protected resources without credentials
- **Guarantee tool selection** - Model decides which tool to use; cannot force specific tool usage (without prompting)
- **Use tools model doesn't support** - Not all models support tool calling; need GPT-4, Claude 3, or similar
