Jest testing patterns for TypeScript:

```markdown

# Jest Testing Skill

## When to Use
When writing unit or integration tests in TypeScript/JavaScript.

## Instructions
Always use async handlers:
\`\`\`typescript
app.get("/users/:id", async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});
\`\`\`
```
