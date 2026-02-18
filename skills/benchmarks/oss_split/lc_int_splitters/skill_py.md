---
name: LangChain Text Splitters Integration (Python)
description: [LangChain] Guide to using text splitter integrations in LangChain including recursive, character, and semantic splitters
---

# langchain-text-splitters (Python)

## Overview

Text splitters divide large documents into smaller chunks that fit within model context windows and enable effective retrieval. Proper chunking is critical for RAG system performance.

### Key Concepts

- **Chunk Size**: Target size for each text chunk (in characters or tokens)
- **Chunk Overlap**: Number of characters/tokens to overlap between chunks
- **Separators**: Characters used to split text
- **Metadata**: Preserved and enriched during splitting

## Splitter Selection Decision Table

| Splitter | Best For | Package | Key Features |
|----------|----------|---------|--------------|
| **RecursiveCharacterTextSplitter** | General purpose | `langchain-text-splitters` | Hierarchical splitting |
| **CharacterTextSplitter** | Simple splitting | `langchain-text-splitters` | Single separator |
| **TokenTextSplitter** | Token-aware | `langchain-text-splitters` | Actual token counts |
| **MarkdownHeaderTextSplitter** | Markdown | `langchain-text-splitters` | Preserves headers |
| **SemanticChunker** | Semantic boundaries | `langchain-experimental` | AI-driven splitting |

### When to Choose Each Splitter

**Choose RecursiveCharacterTextSplitter if:**
- General purpose text (default choice)
- Want to preserve structure
- Need balanced chunks

**Choose TokenTextSplitter if:**
- Need precise token counts
- Character counts unreliable

**Choose SemanticChunker if:**
- Want AI to determine boundaries
- Quality over speed

## Code Examples

### RecursiveCharacterTextSplitter (Recommended)

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

### CharacterTextSplitter

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

### TokenTextSplitter (Token-Aware)

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

### Markdown Splitter

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

### Code Splitter

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# Python code splitter
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
)

python_code = """
def function1():
    pass

class MyClass:
    def method1(self):
        pass
"""

chunks = python_splitter.split_text(python_code)

# JavaScript splitter
js_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size=500,
    chunk_overlap=50,
)
```

### Semantic Chunker (Experimental)

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# AI-driven semantic splitting
splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile"  # or "standard_deviation", "interquartile"
)

chunks = splitter.split_text(text)
# Splits at semantic boundaries, not fixed sizes
```

### Splitting with Vector Store Integration

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader

# Complete RAG pipeline
loader = WebBaseLoader("https://docs.example.com")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_docs = splitter.split_documents(docs)

vectorstore = FAISS.from_documents(
    split_docs,
    OpenAIEmbeddings()
)

# Ready for semantic search
results = vectorstore.similarity_search("query", k=4)
```

### Custom Length Function

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

### Splitting Large PDFs

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

print(f"{len(pages)} pages → {len(chunks)} chunks")

# Metadata includes original page number
for chunk in chunks:
    print(chunk.metadata)
```

## Boundaries

### What Agents CAN Do

✅ **Split text intelligently**
- Recursive splitting to preserve structure
- Configure chunk size and overlap
- Choose separators

✅ **Handle various formats**
- Plain text, markdown, code
- Documents with metadata
- Structured data

✅ **Optimize for use case**
- Balance size vs context
- Token-based splitting
- Semantic splitting

### What Agents CANNOT Do

❌ **Guarantee semantic boundaries**
- Uses heuristics, not perfect understanding
- May split mid-sentence

❌ **Perfectly estimate tokens**
- Character splitters approximate
- Use TokenTextSplitter for exact counts

## Gotchas

### 1. **Chunk Size vs Token Limits**

```python
# ❌ Character count != token count
splitter = RecursiveCharacterTextSplitter(chunk_size=4000)
# May exceed 4096 token limit!

# ✅ Use token-aware splitter
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=4000)
```

**Fix**: Use TokenTextSplitter for token precision.

### 2. **Import from Correct Package**

```python
# ❌ OLD
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ NEW
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

**Fix**: Use `langchain-text-splitters` package.

### 3. **Zero Overlap**

```python
# ❌ No overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,  # Context lost at boundaries
)

# ✅ Use overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 20% overlap
)
```

**Fix**: Always use 10-20% overlap.

### 4. **Metadata Not Preserved**

```python
# ❌ splitText loses metadata
chunks = splitter.split_text(text)

# ✅ Use split_documents
docs = [Document(page_content=text, metadata={"source": "file"})]
chunks = splitter.split_documents(docs)
```

**Fix**: Use `split_documents()` to preserve metadata.

## Links and Resources

### Official Documentation
- [LangChain Python Text Splitters](https://python.langchain.com/docs/integrations/text_splitters/)

### Package Installation
```bash
pip install langchain-text-splitters

# For semantic chunker
pip install langchain-experimental
```
