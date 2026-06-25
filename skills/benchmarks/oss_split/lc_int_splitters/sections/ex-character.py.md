Single separator splitting:

```python
from langchain_text_splitters import CharacterTextSplitter

# Split by single separator
splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = splitter.split_text(text)
```
