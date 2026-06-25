Pytest patterns for fixtures and mocking:

```markdown

# Pytest Patterns Skill

## Fixtures
\`\`\`python
@pytest.fixture
async def db_session():
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()
\`\`\`

## Mocking
Use pytest-mock for external dependencies.
```
