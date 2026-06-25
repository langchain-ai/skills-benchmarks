Tools are functions that agents can execute to perform actions like fetching data, running code, or querying databases. Tools have schemas that describe their purpose and parameters, helping models understand when and how to use them.

Key Concepts:
- **@tool / tool()**: Decorator/function to create tools
- **Schema**: Pydantic models (Python) or Zod schemas (TypeScript) defining parameters
- **Description**: Helps model understand when to use the tool
- **Built-in Tools**: Pre-made tools for common tasks
