BAD: Character vs token mismatch:

```python
# Character count != token count
splitter = RecursiveCharacterTextSplitter(chunk_size=4000)
# May exceed 4096 token limit!

# Use token-aware splitter
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=4000)
```
