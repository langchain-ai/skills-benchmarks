TypeScript factory pattern:

```typescript
function createDatabaseTool(connectionString: string) {
  return tool(
    async ({ query }) => {
      const results = await db.query(query);  // Uses connectionString from closure
      return JSON.stringify(results);
    },
    {
      name: "query_database",
      description: "Execute SQL query on the database",
      schema: z.object({
        query: z.string().describe("SQL query to execute"),
      }),
    }
  );
}

const prodDbTool = createDatabaseTool(process.env.PROD_DB_URL);
const devDbTool = createDatabaseTool(process.env.DEV_DB_URL);
```
