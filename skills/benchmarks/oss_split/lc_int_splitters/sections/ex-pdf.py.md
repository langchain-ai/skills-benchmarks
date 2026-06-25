Load and split PDF pages:

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load PDF
loader = PyPDFLoader("large-document.pdf")
pages = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,
)

chunks = splitter.split_documents(pages)

print(f"{len(pages)} pages -> {len(chunks)} chunks")

# Metadata includes original page number
for chunk in chunks:
    print(chunk.metadata)
```
