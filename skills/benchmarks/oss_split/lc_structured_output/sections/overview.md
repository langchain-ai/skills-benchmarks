Structured output transforms unstructured model responses into validated, typed data. Instead of parsing free text, you get Python objects or JSON conforming to your schema - perfect for extracting data, building forms, or integrating with downstream systems.

Key Concepts:
- **response_format / responseFormat**: Define expected output schema
- **Pydantic Validation (Python)**: Type-safe schemas with automatic validation
- **Zod Validation (TypeScript)**: Type-safe schemas with automatic validation
- **with_structured_output() / withStructuredOutput()**: Model method for direct structured output
- **Tool Strategy**: Uses tool calling under the hood for models without native support
