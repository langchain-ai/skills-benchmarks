Split by header hierarchy:

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

markdown = """
# Header 1
Content 1

## Header 1.1
Content 1.1

# Header 2
Content 2
"""

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)

splits = splitter.split_text(markdown)

# Each split preserves header hierarchy in metadata
for doc in splits:
    print(doc.metadata)
    print(doc.page_content)
```
