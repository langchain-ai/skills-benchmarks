---
name: LangChain Document Loaders Integration (Python)
description: [LangChain] Guide to using document loader integrations in LangChain for PDFs, web pages, text files, and APIs
---

# langchain-document-loaders (Python)

## Overview

Document loaders extract data from various sources and formats into LangChain's standardized Document format. They're essential for building RAG systems, as they convert raw data into processable text chunks with metadata.

### Key Concepts

- **Document**: Object with `page_content` (text) and `metadata` (source info, page numbers, etc.)
- **Loaders**: Classes that extract content from specific sources/formats
- **Metadata**: Contextual information preserved during loading
- **Lazy Loading**: Stream documents without loading everything into memory

## Loader Selection Decision Table

| Loader Type | Best For | Package | Key Features |
|-------------|----------|---------|--------------|
| **PyPDFLoader** | PDF files | `langchain-community` | Page-by-page extraction |
| **WebBaseLoader** | Web pages | `langchain-community` | HTML parsing with BeautifulSoup |
| **TextLoader** | Plain text files | `langchain-community` | Simple text files |
| **JSONLoader** | JSON files/APIs | `langchain-community` | Extract specific JSON fields |
| **CSVLoader** | CSV files | `langchain-community` | Tabular data |
| **DirectoryLoader** | Multiple files | `langchain-community` | Bulk loading from directories |
| **UnstructuredLoader** | Various formats | `langchain-community` | PDFs, DOCXs, PPTs, images |

### When to Choose Each Loader

**Choose PyPDFLoader if:**
- You're processing standard PDF documents
- You need page number metadata
- PDFs contain extractable text

**Choose WebBaseLoader if:**
- You're scraping web pages
- You need to parse HTML content
- You want to filter by CSS selectors

**Choose UnstructuredLoader if:**
- You have mixed document types
- You need OCR for scanned documents
- You want sophisticated parsing

## Code Examples

### PDF Loader

```python
from langchain_community.document_loaders import PyPDFLoader

# Load PDF file
loader = PyPDFLoader("path/to/document.pdf")
docs = loader.load()

print(f"Loaded {len(docs)} pages")
for i, doc in enumerate(docs):
    print(f"Page {i + 1}:", doc.metadata)
    print(doc.page_content[:100])

# Each page is a separate document
# metadata includes: source, page number

# Lazy loading for large PDFs
loader = PyPDFLoader("large-file.pdf")
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata['page']}")
```

### Web Scraping

```python
from langchain_community.document_loaders import WebBaseLoader

# Load single URL
loader = WebBaseLoader("https://docs.langchain.com")
docs = loader.load()

print(docs[0].page_content)
print(docs[0].metadata)  # {'source': url, ...}

# With custom BeautifulSoup parsing
loader = WebBaseLoader(
    "https://news.ycombinator.com",
    bs_kwargs={
        "parse_only": bs4.SoupStrainer(class_=("storylink", "subtext"))
    }
)

# Multiple URLs
loader = WebBaseLoader([
    "https://example.com/page1",
    "https://example.com/page2",
])
docs = loader.load()
```

### Text File Loader

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("path/to/file.txt")
docs = loader.load()

# Returns single document with entire file content
print(docs[0].page_content)
print(docs[0].metadata["source"])  # File path

# With specific encoding
loader = TextLoader("file.txt", encoding="utf-8")
```

### JSON Loader

```python
from langchain_community.document_loaders import JSONLoader
import json

# Load JSON with specific field extraction
loader = JSONLoader(
    file_path="path/to/data.json",
    jq_schema=".texts[].content",  # jq syntax to extract fields
    text_content=False
)

docs = loader.load()

# Example JSON: {"texts": [{"content": "...", "id": 1}]}
# Each matching field becomes a document

# With metadata function
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["id"] = record.get("id")
    metadata["category"] = record.get("category")
    return metadata

loader = JSONLoader(
    file_path="data.json",
    jq_schema=".items[]",
    content_key="text",
    metadata_func=metadata_func
)
```

### CSV Loader

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

### Directory Loader

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Load all text files from directory
loader = DirectoryLoader(
    "path/to/documents",
    glob="**/*.txt",  # Pattern for files to load
    loader_cls=TextLoader
)

docs = loader.load()
print(f"Loaded {len(docs)} documents")

# With multiple file types
from langchain_community.document_loaders import PyPDFLoader

# Custom loader for different file types
def get_loader(file_path):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        return TextLoader(file_path)
```

### Unstructured Loader (Advanced)

```python
from langchain_community.document_loaders import UnstructuredFileLoader

# Handles PDFs, DOCXs, PPTs, images, etc.
loader = UnstructuredFileLoader("path/to/document.docx")
docs = loader.load()

# With OCR for scanned documents
loader = UnstructuredFileLoader(
    "scanned.pdf",
    strategy="ocr_only",  # Use OCR
    languages=["eng"]
)

# UnstructuredURLLoader for web pages
from langchain_community.document_loaders import UnstructuredURLLoader

loader = UnstructuredURLLoader(urls=["https://example.com"])
docs = loader.load()
```

### S3 Loader (Cloud Storage)

```python
from langchain_community.document_loaders import S3FileLoader

loader = S3FileLoader(
    bucket="my-bucket",
    key="documents/file.pdf"
)
docs = loader.load()

# S3 Directory Loader
from langchain_community.document_loaders import S3DirectoryLoader

loader = S3DirectoryLoader(
    bucket="my-bucket",
    prefix="documents/"
)
docs = loader.load()
```

### Custom Metadata Example

```python
from langchain_community.document_loaders import TextLoader
from datetime import datetime

loader = TextLoader("document.txt")
docs = loader.load()

# Enrich with custom metadata
for doc in docs:
    doc.metadata["loaded_at"] = datetime.now().isoformat()
    doc.metadata["category"] = "research"
```

### Lazy Loading (Memory Efficient)

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("large-file.pdf")

# Stream documents one at a time
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata.get('page', 0)}")
    # Process without loading all pages into memory
```

## Boundaries

### What Agents CAN Do

✅ **Load from various sources**
- PDF, text, CSV, JSON, DOCX, PPTX files
- Web pages and URLs
- Cloud storage (S3, GCS, Azure)
- APIs and databases

✅ **Extract with metadata**
- Preserve source information
- Add custom metadata
- Track page numbers, URLs, timestamps

✅ **Process efficiently**
- Use lazy loading for large files
- Batch process directories
- Stream data

✅ **Customize extraction**
- Use jq for JSON extraction
- BeautifulSoup for HTML parsing
- OCR for scanned documents

### What Agents CANNOT Do

❌ **Extract from encrypted/protected files**
- Cannot bypass password-protected PDFs
- Cannot access auth-required sites without credentials

❌ **Process all formats automatically**
- Scanned PDFs need OCR
- Proprietary formats need specific loaders

❌ **Bypass rate limits**
- Must respect website rate limiting

## Gotchas

### 1. **Import from Correct Package**

```python
# ❌ OLD: Using langchain imports
from langchain.document_loaders import PyPDFLoader  # Deprecated!

# ✅ NEW: Use community package
from langchain_community.document_loaders import PyPDFLoader
```

**Fix**: Use `langchain-community` package.

### 2. **PyPDF vs Unstructured**

```python
# ❌ PyPDF may not work for complex PDFs
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("complex.pdf")
docs = loader.load()  # Poor extraction!

# ✅ Use Unstructured for complex PDFs
from langchain_community.document_loaders import UnstructuredPDFLoader
loader = UnstructuredPDFLoader("complex.pdf")
docs = loader.load()  # Better extraction
```

**Fix**: Use UnstructuredPDFLoader for complex layouts.

### 3. **Web Scraping Dependencies**

```python
# ❌ Missing dependencies
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
# ImportError: bs4 not found!

# ✅ Install required packages
# pip install beautifulsoup4 lxml
```

**Fix**: Install `beautifulsoup4` and `lxml`.

### 4. **Unstructured API Keys**

```python
# ❌ Unstructured may need API key for advanced features
from langchain_community.document_loaders import UnstructuredFileLoader
loader = UnstructuredFileLoader("file.pdf", strategy="ocr_only")
# May fail without API key!

# ✅ Set API key or install dependencies
# pip install unstructured[local-inference]
# Or set UNSTRUCTURED_API_KEY environment variable
```

**Fix**: Install local dependencies or use API key.

### 5. **Encoding Issues**

```python
# ❌ Default encoding may fail
loader = TextLoader("file.txt")
docs = loader.load()  # UnicodeDecodeError!

# ✅ Specify encoding
loader = TextLoader("file.txt", encoding="utf-8")
docs = loader.load()
```

**Fix**: Specify correct encoding for text files.

### 6. **S3 Credentials**

```python
# ❌ Missing AWS credentials
from langchain_community.document_loaders import S3FileLoader
loader = S3FileLoader("bucket", "key")
docs = loader.load()  # Credential error!

# ✅ Configure AWS credentials
# Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# Or use AWS CLI: aws configure
```

**Fix**: Configure AWS credentials properly.

## Links and Resources

### Official Documentation
- [LangChain Python Document Loaders](https://python.langchain.com/docs/integrations/document_loaders/)
- [PDF Loaders](https://python.langchain.com/docs/integrations/document_loaders/#pdfs)
- [Web Loaders](https://python.langchain.com/docs/integrations/document_loaders/#web)

### Package Installation
```bash
# Community loaders
pip install langchain-community

# PDF support
pip install pypdf

# Web scraping
pip install beautifulsoup4 lxml

# Unstructured (advanced)
pip install unstructured
# or with local inference
pip install "unstructured[local-inference]"
```
