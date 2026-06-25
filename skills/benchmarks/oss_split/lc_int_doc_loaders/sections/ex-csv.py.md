CSV rows as documents:

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="path/to/data.csv",
    source_column="source",  # Column for metadata
)

docs = loader.load()

# Each row becomes a document
# All columns stored in metadata
```
