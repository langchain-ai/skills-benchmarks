Require human approval before executing sensitive tools like delete operations.
```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

@tool
def delete_record(record_id: str) -> str:
    """Delete a database record permanently.

    Args:
        record_id: ID of record to delete
    """
    db.delete(record_id)
    return f"Deleted record {record_id}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[delete_record, search],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"delete_record": True}
        )
    ],
)
```
