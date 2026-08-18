Production-ready async persistence:

```python
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def main():
    # Create async Postgres checkpointer
    async with AsyncPostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/db"
    ) as checkpointer:
        graph = (
            StateGraph(State)
            .add_node("process", process_node)
            .add_edge(START, "process")
            .add_edge("process", END)
            .compile(checkpointer=checkpointer)
        )

        config = {"configurable": {"thread_id": "thread-1"}}
        result = await graph.ainvoke({"data": "test"}, config)
```
