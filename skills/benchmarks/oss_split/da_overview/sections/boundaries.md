**What Agents CAN Configure:**
- Model selection and parameters
- Additional custom tools
- System prompt customization
- Backend storage strategy
- Which tools require approval
- Custom subagents with specialized tools
- Skill directories and content
- Middleware order and configuration

**What Agents CANNOT Configure:**
- Core middleware removal (TodoList, Filesystem, SubAgent are always present)
- The write_todos, task, or filesystem tool names
- The fundamental tool-calling loop
- LangGraph's runtime execution model
- The Agent Skills protocol format
