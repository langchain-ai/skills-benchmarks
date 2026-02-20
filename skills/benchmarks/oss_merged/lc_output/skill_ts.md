---
name: LangChain Structured Output & HITL (TypeScript)
description: "INVOKE THIS SKILL when you need structured/typed output from LLMs OR human-in-the-loop approval. Covers with_structured_output(), Zod schemas, union types for multiple formats, and HITL middleware. CRITICAL: Fixes for accessing structured response wrong, missing field descriptions, and schema validation errors."
---

<overview>
Two critical patterns for production agents:

1. **Structured Output**: Transform unstructured model responses into validated, typed data using Zod schemas
2. **Human-in-the-Loop**: Add human oversight to agent tool calls, pausing for approval before sensitive actions

**Key Concepts:**
- **withStructuredOutput()**: Model method for direct structured output
- **Zod schemas**: Define expected output structure and validation
- **interruptBefore**: Pauses execution before specified tools for human decisions
- **Interrupts**: Checkpoint where agent waits for human input
</overview>

<when-to-use-structured-output>

| Use Case | Use Structured Output? | Why |
|----------|----------------------|-----|
| Extract contact info, dates, etc. | Yes | Reliable data extraction |
| Form filling | Yes | Validate all required fields |
| API integration | Yes | Type-safe responses |
| Classification tasks | Yes | Enum validation |
| Open-ended Q&A | No | Free-form text is fine |

</when-to-use-structured-output>

---

## Structured Output

<ex-basic-structured-output>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string(),
});

const model = new ChatOpenAI({ model: "gpt-4" });
const structuredModel = model.withStructuredOutput(ContactInfo);

const response = await structuredModel.invoke(
  "Extract: John Doe, john@example.com, (555) 123-4567"
);
console.log(response);
// { name: 'John Doe', email: 'john@example.com', phone: '(555) 123-4567' }
```
</ex-basic-structured-output>

<ex-model-direct-structured-output>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const Movie = z.object({
  title: z.string().describe("Movie title"),
  year: z.number().describe("Release year"),
  director: z.string(),
  rating: z.number().min(0).max(10),
});

const model = new ChatOpenAI({ model: "gpt-4" });
const structuredModel = model.withStructuredOutput(Movie);

const response = await structuredModel.invoke("Tell me about Inception");
// { title: "Inception", year: 2010, director: "Christopher Nolan", rating: 8.8 }
```
</ex-model-direct-structured-output>

<ex-enum-and-literal-types>
```typescript
import { z } from "zod";

const Classification = z.object({
  category: z.enum(["urgent", "normal", "low"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  confidence: z.number().min(0).max(1),
});
```
</ex-enum-and-literal-types>

---

## Human-in-the-Loop

<ex-basic-hitl-setup>
```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const sendEmail = tool(
  async ({ to, subject, body }) => `Email sent to ${to}`,
  {
    name: "send_email",
    description: "Send an email",
    schema: z.object({ to: z.string(), subject: z.string(), body: z.string() }),
  }
);

const agent = createReactAgent({
  llm: model,
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required for HITL
  interruptBefore: ["send_email"],
});
```
</ex-basic-hitl-setup>

<ex-running-with-interrupts>
```typescript
import { Command } from "@langchain/langgraph";

const config = { configurable: { thread_id: "session-1" } };

// Step 1: Agent runs until it needs to call tool
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "Send email to john@example.com" }]
}, config);

// Check for interrupt
if (result1.__interrupt__) {
  console.log(`Waiting for approval: ${result1.__interrupt__}`);
}

// Step 2: Human approves
const result2 = await agent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  config
);
```
</ex-running-with-interrupts>

<boundaries>
### What You CAN Configure

**Structured Output:**
- Schema structure: Any valid Zod schema
- Field validation: Types, ranges, regex, etc.
- Nested objects, arrays, enums

**HITL:**
- Which tools require approval via interruptBefore
- Checkpointer for persistence

### What You CANNOT Configure

- Model reasoning: Can't control how model generates data
- Guarantee 100% accuracy: Model may still make mistakes
- Skip checkpointer requirement for HITL
</boundaries>

<fix-accessing-response-wrong>
```typescript
// With withStructuredOutput, response IS the structured data
const response = await structuredModel.invoke("...");
console.log(response);  // Directly the parsed object
```
</fix-accessing-response-wrong>

<fix-missing-descriptions>
```typescript
// WRONG: No descriptions
const Data = z.object({
  date: z.string(),
  amount: z.number(),
});

// CORRECT: Add descriptions
const Data = z.object({
  date: z.string().describe("Date in YYYY-MM-DD format"),
  amount: z.number().describe("Amount in USD"),
});
```
</fix-missing-descriptions>

<fix-missing-checkpointer>
```typescript
// WRONG: No checkpointer for HITL
const agent = createReactAgent({
  llm: model,
  tools: [sendEmail],
  interruptBefore: ["send_email"],  // Will fail!
});

// CORRECT: Always add checkpointer
import { MemorySaver } from "@langchain/langgraph";

const agent = createReactAgent({
  llm: model,
  tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required
  interruptBefore: ["send_email"],
});
```
</fix-missing-checkpointer>

<fix-wrong-resume-syntax>
```typescript
// WRONG: Wrong resume format
await agent.invoke({ resume: { decisions: [...] } });  // Wrong!

// CORRECT: Use Command
import { Command } from "@langchain/langgraph";

await agent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  config
);
```
</fix-wrong-resume-syntax>
