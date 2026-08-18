Streaming progress updates:

```python
from langchain.tools import tool

@tool
async def process_large_file(filepath: str, runtime) -> str:
    """Process a large file with progress updates.

    Args:
        filepath: Path to file to process
    """
    total_lines = 1000

    for i in range(0, total_lines, 100):
        await runtime.stream_writer.write({
            "type": "progress",
            "data": {"processed": i, "total": total_lines},
        })
        await process_chunk(i, i + 100)

    return "Processing complete"
```
