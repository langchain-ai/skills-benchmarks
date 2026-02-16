# Skills Project Guidelines

## Python/TypeScript Parity

**CRITICAL:** LangSmith skills have both Python and TypeScript implementations. These MUST stay in sync:
- Same CLI commands, flags, and options
- Same output format for identical inputs
- Same error handling behavior

When modifying any script, always update both Python and TypeScript versions together. Parity tests in `tests/scripts/langsmith/parity/` verify this.
