Two critical patterns for production agents:

1. **Structured Output**: Transform unstructured model responses into validated, typed data
2. **Human-in-the-Loop**: Add human oversight to agent tool calls, pausing for approval

**Key Concepts:**
- **response_format**: Define expected output schema
- **with_structured_output()**: Model method for direct structured output
- **HumanInTheLoopMiddleware**: Pauses execution for human decisions
