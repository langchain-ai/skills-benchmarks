Basic store CRUD operations:

```typescript
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Put (create/update)
await store.put(
  ["user-123", "facts"],
  "location",
  { city: "San Francisco", country: "USA" }
);

// Get
const item = await store.get(["user-123", "facts"], "location");
console.log(item);  // { city: 'San Francisco', country: 'USA' }

// Search with filters
const results = await store.search(
  ["user-123", "facts"],
  { filter: { country: "USA" } }
);

// Delete
await store.delete(["user-123", "facts"], "location");
```
