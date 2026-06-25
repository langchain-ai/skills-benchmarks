Create class-based tool extending StructuredTool.

```typescript
import { StructuredTool } from "@langchain/core/tools";
import { z } from "zod";

class DatabaseQueryTool extends StructuredTool {
  name = "database_query";
  description = "Query the customer database for information";

  schema = z.object({
    customerId: z.string().describe("Customer ID to look up"),
  });

  async _call({ customerId }: { customerId: string }): Promise<string> {
    // Your database logic
    const customer = await db.getCustomer(customerId);
    return JSON.stringify(customer);
  }
}

const dbTool = new DatabaseQueryTool();
```
