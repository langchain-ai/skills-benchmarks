Tool calling allows chat models to request execution of external functions. Models decide which tools to call based on user input, and the results are passed back to the model for further reasoning. This is the foundation of agentic behavior.

Key Concepts:
- **bind_tools() / bindTools()**: Attach tools to a model
- **Tool Calls**: Model requests to execute tools (in AIMessage.tool_calls)
- **Tool Messages**: Results passed back to model (ToolMessage)
- **Tool Choice**: Control which tools the model can use
