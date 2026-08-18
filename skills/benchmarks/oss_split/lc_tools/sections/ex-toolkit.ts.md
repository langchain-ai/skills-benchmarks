TypeScript toolkit object:

```typescript
const emailTools = {
  send: tool(
    async ({ to, subject, body }) => `Email sent to ${to}`,
    {
      name: "send_email",
      description: "Send an email message",
      schema: z.object({
        to: z.string().email(),
        subject: z.string(),
        body: z.string(),
      }),
    }
  ),

  read: tool(
    async ({ folder, limit }) => `Retrieved ${limit} emails from ${folder}`,
    {
      name: "read_emails",
      description: "Read emails from a folder",
      schema: z.object({
        folder: z.string().default("inbox"),
        limit: z.number().default(10),
      }),
    }
  ),
};

const agent = createAgent({
  model: "gpt-4.1",
  tools: Object.values(emailTools),
});
```
