---
name: langchain-text-splitters-integration-py
description: "[LangChain] Guide to using text splitter integrations in LangChain including recursive, character, and semantic splitters"
---

<overview>
Text splitters divide large documents into smaller chunks that fit within model context windows and enable effective retrieval. Proper chunking is critical for RAG system performance.

### Key Concepts

- **Chunk Size**: Target size for each text chunk (in characters or tokens)
- **Chunk Overlap**: Number of characters/tokens to overlap between chunks
- **Separators**: Characters used to split text
- **Metadata**: Preserved and enriched during splitting
</overview>

<splitter-selection>

| Splitter | Best For | Package | Key Features |
|----------|----------|---------|--------------|
| **RecursiveCharacterTextSplitter** | General purpose | `langchain-text-splitters` | Hierarchical splitting |
| **CharacterTextSplitter** | Simple splitting | `langchain-text-splitters` | Single separator |
| **TokenTextSplitter** | Token-aware | `langchain-text-splitters` | Actual token counts |
| **MarkdownHeaderTextSplitter** | Markdown | `langchain-text-splitters` | Preserves headers |
| **SemanticChunker** | Semantic boundaries | `langchain-experimental` | AI-driven splitting |

</splitter-selection>

<when-to-choose>
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
</when-to-choose>

<ex-recursive-character-text-splitter>
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
</ex-recursive-character-text-splitter>

<ex-character-text-splitter>
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
</ex-character-text-splitter>

<ex-token-text-splitter>
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
</ex-token-text-splitter>

<ex-markdown-splitter>
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
</ex-markdown-splitter>

<ex-code-splitter>
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
</ex-code-splitter>

<ex-semantic-chunker>
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
</ex-semantic-chunker>

<ex-vector-store-integration>
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
</ex-vector-store-integration>

<ex-custom-length-function>
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
</ex-custom-length-function>

<ex-splitting-large-pdfs>
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
</ex-splitting-large-pdfs>

<boundaries>
### What Agents CAN Do

* Split text intelligently**
- Recursive splitting to preserve structure
- Configure chunk size and overlap
- Choose separators

* Handle various formats**
- Plain text, markdown, code
- Documents with metadata
- Structured data

* Optimize for use case**
- Balance size vs context
- Token-based splitting
- Semantic splitting

### What Agents CANNOT Do

* Guarantee semantic boundaries**
- Uses heuristics, not perfect understanding
- May split mid-sentence

* Perfectly estimate tokens**
- Character splitters approximate
- Use TokenTextSplitter for exact counts
</boundaries>

<fix-chunk-size-vs-token-limits>
```python
# WRONG: Character count != token count
splitter = RecursiveCharacterTextSplitter(chunk_size=4000)
# May exceed 4096 token limit!

# CORRECT: Use token-aware splitter
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=4000)
```
</fix-chunk-size-vs-token-limits>

<fix-import-from-correct-package>
```python
# WRONG: OLD
from langchain.text_splitter import RecursiveCharacterTextSplitter

# CORRECT: NEW
from langchain_text_splitters import RecursiveCharacterTextSplitter
```
</fix-import-from-correct-package>

<fix-zero-overlap>
```python
# WRONG: No overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,  # Context lost at boundaries
)

# CORRECT: Use overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 20% overlap
)
```
</fix-zero-overlap>

<fix-metadata-not-preserved>
```python
# WRONG: splitText loses metadata
chunks = splitter.split_text(text)

# CORRECT: Use split_documents
docs = [Document(page_content=text, metadata={"source": "file"})]
chunks = splitter.split_documents(docs)
```
</fix-metadata-not-preserved>

<installation>
```bash
pip install langchain-text-splitters

# For semantic chunker
pip install langchain-experimental
```
</installation>

<links>
- [LangChain Python Text Splitters](https://python.langchain.com/docs/integrations/text_splitters/)
</links>
