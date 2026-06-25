Add safety checks before deployment:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool

@tool
def run_tests(test_suite: str) -> str:
    """Run a test suite."""
    return f"Tests in {test_suite} passed"

@tool
def deploy_code(environment: str) -> str:
    """Deploy code to an environment."""
    return f"Deployed to {environment}"

agent = create_agent(
    model="gpt-4",
    tools=[run_tests, deploy_code],
    middleware=[
        TodoListMiddleware(
            system_prompt="""For deployment tasks, always:
            1. Create a todo list with safety checks
            2. Run tests before deployment
            3. Mark each step as completed before proceeding
            """,
        ),
    ],
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Deploy the application to production"
    }]
})
```
