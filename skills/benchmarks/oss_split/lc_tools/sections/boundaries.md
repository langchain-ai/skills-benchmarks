What You CAN Configure:
- **Function logic**: Any Python/TypeScript code
- **Parameters**: Via type hints/Pydantic (Python) or Zod schemas (TypeScript)
- **Name and description**: Guide model's tool selection
- **Return value**: Any serializable data (string, JSON, etc.)
- **Async operations**: Tools can be async
- **Error handling**: Raise exceptions or return error messages

What You CANNOT Configure:
- **When model calls tool**: Model decides based on context
- **Tool call order**: Model determines execution flow
- **Parameter values**: Model generates based on schema
- **Response format from model**: Tool returns, model interprets
