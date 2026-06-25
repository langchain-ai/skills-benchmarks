Recursive splitter with overlap:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Basic usage
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    add_start_index=True,  # Adds start_index to metadata
)

text = "Long document text here..."
chunks = splitter.split_text(text)

print(f"Created {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}: {len(chunk)} characters")

# Split documents (preserves metadata)
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Long text...",
        metadata={"source": "doc1.pdf", "page": 1}
    )
]

split_docs = splitter.split_documents(docs)
# Metadata preserved and enriched
print(split_docs[0].metadata)
```
