Agents combine language models with tools to create systems that can reason, act, and iterate.

**Key Components:**
- **@tool / tool()**: Create tools from functions
- **bind_tools()**: Attach tools to a model
- **Tool Calls**: Model requests in AIMessage.tool_calls
- **ToolMessage**: Results passed back to model
- **create_agent()**: Production-ready agent built on LangGraph
