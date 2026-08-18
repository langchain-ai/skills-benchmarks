Custom tiktoken length function:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# Use actual token counter
def tiktoken_len(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=tiktoken_len,
)
```
