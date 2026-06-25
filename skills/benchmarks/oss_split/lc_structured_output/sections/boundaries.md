What You CAN Configure:
- **Schema structure**: Any valid Pydantic model or Zod schema
- **Field validation**: Types, ranges, regex, etc.
- **Optional vs required**: Control field presence
- **Nested objects**: Complex hierarchies
- **Arrays**: Lists of items
- **Enums**: Restricted values with Literal/z.enum

What You CANNOT Configure:
- **Model reasoning**: Can't control how model generates data
- **Guarantee 100% accuracy**: Model may still make mistakes
- **Force valid data if context lacks it**: Model can't invent missing info
