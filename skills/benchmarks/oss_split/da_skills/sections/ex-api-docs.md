API documentation skill example:

```markdown

# FastAPI Documentation Skill

## Endpoints
Always use async handlers:
\`\`\`python
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
\`\`\`

## Validation
Use Pydantic models for request/response validation.

## Supporting Files
See endpoints.py for complete examples.
```
