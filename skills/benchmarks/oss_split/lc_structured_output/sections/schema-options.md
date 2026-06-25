| Schema Type | Language | When to Use | Example |
|-------------|----------|-------------|---------|
| Pydantic model | Python | Python projects (recommended) | `class Model(BaseModel):` |
| Zod schema | TypeScript | TypeScript projects (recommended) | `z.object({...})` |
| TypedDict | Python | Simpler typing | `class Data(TypedDict):` |
| JSON Schema | Both | Interoperability | `{"type": "object", ...}` |
| Union types | Both | Multiple possible formats | `Union[Schema1, Schema2]` / `z.union([...])` |
