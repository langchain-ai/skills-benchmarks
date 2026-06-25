Token-based splitting:

```python
from langchain_text_splitters import TokenTextSplitter

# Split based on actual tokens
splitter = TokenTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
)

chunks = splitter.split_text(text)

# Uses tiktoken for OpenAI token counting
# More accurate than character counting
```
