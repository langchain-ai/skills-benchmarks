Emit custom progress from tools:

```python
from langchain.tools import tool

@tool
async def process_data(data: list, runtime) -> str:
    """Process data with progress updates."""
    total = len(data)

    for i in range(0, total, 100):
        # Emit custom progress update
        await runtime.stream_writer.write({
            "type": "progress",
            "data": {
                "processed": i,
                "total": total,
                "percentage": (i / total) * 100,
            },
        })

        # Do actual processing
        await process_chunk(data[i:i+100])

    return "Processing complete"

# Stream custom updates
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Process this data"}]},
    stream_mode=["custom", "updates"],
):
    if mode == "custom":
        print(f"Progress: {chunk['data']['percentage']}%")
```
