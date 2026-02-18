---
name: LangChain Structured Output (TypeScript)
description: [LangChain] Get structured, validated output from LangChain agents and models using Pydantic schemas, type-safe responses, and automatic validation
---

# langchain-structured-output (JavaScript/TypeScript)

## Overview

Structured output transforms unstructured model responses into validated, typed data. Instead of parsing free text, you get JSON objects conforming to your schema - perfect for extracting data, building forms, or integrating with downstream systems.

**Key Concepts:**
- **responseFormat**: Define expected output schema
- **Zod Validation**: Type-safe schemas with automatic validation
- **withStructuredOutput()**: Model method for direct structured output
- **Tool Strategy**: Uses tool calling under the hood for models without native support

## Decision Tables

### When to Use Structured Output

| Use Case | Use Structured Output? | Why |
|----------|----------------------|-----|
| Extract contact info, dates, etc. | ✅ Yes | Reliabledata extraction |
| Form filling | ✅ Yes | Validate all required fields |
| API integration | ✅ Yes | Type-safe responses |
| Classification tasks | ✅ Yes | Enum validation |
| Open-ended Q&A | ❌ No | Free-form text is fine |
| Creative writing | ❌ No | Don't constrain creativity |

### Schema Options

| Schema Type | When to Use | Example |
|-------------|-------------|---------|
| Zod schema | TypeScript projects (recommended) | `z.object({...})` |
| JSON Schema | Interoperability | `{ type: "object", properties: {...} }` |
| Union types | Multiple possible formats | `z.union([schema1, schema2])` |

## Code Examples

### Basic Structured Output with Agent

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string(),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactInfo,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract: John Doe, john@example.com, (555) 123-4567"
  }],
});

console.log(result.structuredResponse);
// { name: 'John Doe', email: 'john@example.com', phone: '(555) 123-4567' }
```

### Model Direct Structured Output

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const MovieSchema = z.object({
  title: z.string().describe("Movie title"),
  year: z.number().describe("Release year"),
  director: z.string(),
  rating: z.number().min(0).max(10),
});

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(MovieSchema);

const response = await structuredModel.invoke("Tell me about Inception");
console.log(response);
// { title: "Inception", year: 2010, director: "Christopher Nolan", rating: 8.8 }
```

### Complex Nested Schema

```typescript
import { z } from "zod";

const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string(),
  zip: z.string(),
});

const PersonSchema = z.object({
  name: z.string(),
  age: z.number().int().positive(),
  email: z.string().email(),
  address: AddressSchema,
  tags: z.array(z.string()),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: PersonSchema,
});
```

### Enum and Literal Types

```typescript
import { z } from "zod";

const ClassificationSchema = z.object({
  category: z.enum(["urgent", "normal", "low"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  confidence: z.number().min(0).max(1),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ClassificationSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Classify: This is extremely important and I'm very happy!"
  }],
});
// { category: "urgent", sentiment: "positive", confidence: 0.95 }
```

### Optional Fields and Defaults

```typescript
import { z } from "zod";

const EventSchema = z.object({
  title: z.string(),
  date: z.string(),
  location: z.string().optional(),
  attendees: z.array(z.string()).default([]),
  confirmed: z.boolean().default(false),
});
```

### Union Types (Multiple Schemas)

```typescript
import { z } from "zod";

const EmailSchema = z.object({
  type: z.literal("email"),
  to: z.string().email(),
  subject: z.string(),
});

const PhoneSchema = z.object({
  type: z.literal("phone"),
  number: z.string(),
  message: z.string(),
});

const ContactSchema = z.union([EmailSchema, PhoneSchema]);

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: ContactSchema,
});
// Model chooses which schema based on input
```

### Array Extraction

```typescript
import { z } from "zod";

const TaskListSchema = z.object({
  tasks: z.array(z.object({
    title: z.string(),
    priority: z.enum(["high", "medium", "low"]),
    dueDate: z.string().optional(),
  })),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: TaskListSchema,
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Extract tasks: 1. Fix bug (high priority, due tomorrow) 2. Update docs"
  }],
});
```

### Include Raw AIMessage

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const schema = z.object({ name: z.string(), age: z.number() });

const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(schema, {
  includeRaw: true,
});

const response = await structuredModel.invoke("Person: Alice, 30 years old");
console.log(response);
// {
//   raw: AIMessage { ... },
//   parsed: { name: "Alice", age: 30 }
// }
```

### Error Handling

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

const StrictSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(120),
});

const agent = createAgent({
  model: "gpt-4.1",
  responseFormat: StrictSchema,
});

try {
  const result = await agent.invoke({
    messages: [{ role: "user", content: "Email: invalid, Age: -5" }],
  });
} catch (error) {
  console.error("Validation failed:", error);
  // Model will retry or return error
}
```

## Boundaries

### What You CAN Configure

✅ **Schema structure**: Any valid Zod schema
✅ **Field validation**: Types, ranges, regex, etc.
✅ **Optional vs required**: Control field presence
✅ **Nested objects**: Complex hierarchies
✅ **Arrays**: Lists of items
✅ **Enums**: Restricted values

### What You CANNOT Configure

❌ **Model reasoning**: Can't control how model generates data
❌ **Guarantee 100% accuracy**: Model may still make mistakes
❌ **Force valid data if context lacks it**: Model can't invent missing info

## Gotchas

### 1. Accessing Response Wrong

```typescript
// ❌ Problem: Accessing wrong property
const result = await agent.invoke(input);
console.log(result.response);  // undefined!

// ✅ Solution: Use structuredResponse
console.log(result.structuredResponse);
```

### 2. Missing Descriptions

```typescript
// ❌ Problem: No field descriptions
const schema = z.object({
  date: z.string(),  // What format?
  amount: z.number(),  // What unit?
});

// ✅ Solution: Add descriptions
const schema = z.object({
  date: z.string().describe("Date in YYYY-MM-DD format"),
  amount: z.number().describe("Amount in USD"),
});
```

### 3. Over-constraining

```typescript
// ❌ Problem: Too strict for model
const schema = z.object({
  code: z.string().regex(/^[A-Z]{2}-\d{4}-[A-Z]{3}$/),  // Very specific!
});

// ✅ Solution: Validate post-processing or use looser schema
const schema = z.object({
  code: z.string().describe("Format: XX-0000-XXX (letters and numbers)"),
});
```

### 4. Not Handling Validation Errors

```typescript
// ❌ Problem: No error handling
const result = await agent.invoke(input);
const data = result.structuredResponse;  // May throw!

// ✅ Solution: Try/catch or check for errors
try {
  const result = await agent.invoke(input);
  const data = result.structuredResponse;
} catch (error) {
  console.error("Failed to get structured output:", error);
}
```

### 5. Confusing responseFormat with tools

```typescript
// ❌ Problem: Using responseFormat with tools incorrectly
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  responseFormat: MySchema,  // Will extract from FINAL response only
});
// Tools run first, then schema extracted from final response

// ✅ This is correct if you want tools + structured final output
// Just understand the flow
```

## Links to Documentation

- [Structured Output Overview](https://docs.langchain.com/oss/javascript/langchain/structured-output)
- [Model Structured Output](https://docs.langchain.com/oss/javascript/langchain/models)
- [Agent Structured Output](https://docs.langchain.com/oss/javascript/langchain/agents)
