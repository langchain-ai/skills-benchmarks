Returning JSON-serialized data:

```python
from langchain.tools import tool
import json

@tool
def analyze_text(text: str) -> str:
    """Analyze text statistics.

    Args:
        text: Text to analyze
    """
    words = text.split()

    stats = {
        "word_count": len(words),
        "char_count": len(text),
        "sentences": len(text.split(".")),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
    }

    return json.dumps(stats)
```
