JSON with jq extraction:

```python
from langchain_community.document_loaders import JSONLoader
import json

# Load JSON with specific field extraction
loader = JSONLoader(
    file_path="path/to/data.json",
    jq_schema=".texts[].content",  # jq syntax to extract fields
    text_content=False
)

docs = loader.load()

# Example JSON: {"texts": [{"content": "...", "id": 1}]}
# Each matching field becomes a document

# With metadata function
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["id"] = record.get("id")
    metadata["category"] = record.get("category")
    return metadata

loader = JSONLoader(
    file_path="data.json",
    jq_schema=".items[]",
    content_key="text",
    metadata_func=metadata_func
)
```
