Deep Agents are an opinionated agent framework built on LangChain/LangGraph with built-in middleware:

- **Task Planning**: TodoListMiddleware for breaking down complex tasks
- **Context Management**: Filesystem tools with pluggable backends
- **Task Delegation**: SubAgent middleware for spawning specialized agents
- **Long-term Memory**: Persistent storage across threads via Store
- **Human-in-the-loop**: Approval workflows for sensitive operations
- **Skills**: On-demand loading of specialized capabilities

The agent harness provides these capabilities automatically - you configure, not implement.
