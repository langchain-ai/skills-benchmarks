Tool with filesystem side effects:

```python
from langchain.tools import tool
from pathlib import Path

@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.

    Use carefully as this modifies the filesystem.

    Args:
        filepath: Path to the file
        content: Content to write
    """
    Path(filepath).write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to {filepath}"
```
