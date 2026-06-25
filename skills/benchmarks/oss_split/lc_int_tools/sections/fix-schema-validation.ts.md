Use specific Zod types, not z.any().

```typescript
// No schema validation
const myTool = tool(
  async ({ location }) => {
    // Assumes location is a string, but no validation
    return location.toUpperCase(); // Could crash!
  },
  {
    name: "format_location",
    description: "Format location",
    schema: z.object({ location: z.any() }), // Too permissive
  }
);

// Proper schema
const myTool = tool(
  async ({ location }) => {
    return location.toUpperCase();
  },
  {
    name: "format_location",
    description: "Format location name to uppercase",
    schema: z.object({
      location: z.string().describe("Location name"),
    }),
  }
);
```
