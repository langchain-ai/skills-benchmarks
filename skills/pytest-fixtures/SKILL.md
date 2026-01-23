# Pytest Fixtures Skill

Create reusable test fixtures following modern pytest patterns.

## Quick Start

```python
import pytest

@pytest.fixture
def sample_data():
    """Fixture that provides test data."""
    return {"name": "test", "value": 42}
```

## Fixture Scopes

Control when fixtures are created/destroyed:

```python
@pytest.fixture(scope="function")  # Default: new for each test
def per_test_db():
    db = create_db()
    yield db
    db.cleanup()

@pytest.fixture(scope="module")  # Once per test file
def shared_client():
    client = Client()
    yield client
    client.close()

@pytest.fixture(scope="session")  # Once per test run
def global_config():
    return load_config()
```

## Async Fixtures

Use pytest-asyncio for async fixtures:

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    """IMPORTANT: Use @pytest_asyncio.fixture, not @pytest.fixture"""
    client = await AsyncClient.connect()
    yield client
    await client.disconnect()
```

## Database Fixtures with Rollback

For database testing, use transaction rollback pattern:

```python
@pytest.fixture
def db_session(engine):
    """Create a session with automatic rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # IMPORTANT: Rollback, don't commit
    connection.close()
```

## Fixture Factories

When you need multiple similar fixtures:

```python
@pytest.fixture
def make_user():
    """Factory fixture for creating test users."""
    created_users = []

    def _make_user(name: str, role: str = "user"):
        user = User(name=name, role=role)
        created_users.append(user)
        return user

    yield _make_user

    # Cleanup all created users
    for user in created_users:
        user.delete()
```

## Common Gotchas

1. **Async fixtures**: Must use `@pytest_asyncio.fixture`, not `@pytest.fixture`
2. **Scope mismatch**: Can't use function-scoped fixture in session-scoped fixture
3. **Cleanup order**: Use `yield` not `return` when cleanup is needed
4. **autouse pitfall**: `autouse=True` runs for EVERY test - use sparingly

## Conftest.py Placement

```
tests/
  conftest.py       # Fixtures available to all tests
  unit/
    conftest.py     # Fixtures only for unit tests
    test_models.py
  integration/
    conftest.py     # Fixtures only for integration tests
    test_api.py
```
