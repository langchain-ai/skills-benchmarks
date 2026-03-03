---
name: langchain-document-loaders-integration-py
description: "[LangChain] Guide to using document loader integrations in LangChain for PDFs, web pages, text files, and APIs"
---

<overview>
Document loaders extract data from various sources and formats into LangChain's standardized Document format. They're essential for building RAG systems, as they convert raw data into processable text chunks with metadata.

**Key Concepts:**
- **Document**: Object with `page_content` (text) and `metadata` (source info, page numbers, etc.)
- **Loaders**: Classes that extract content from specific sources/formats
- **Metadata**: Contextual information preserved during loading
- **Lazy Loading**: Stream documents without loading everything into memory
</overview>

<loader-selection>

| Loader Type | Best For | Package | Key Features |
|-------------|----------|---------|--------------|
| **PyPDFLoader** | PDF files | `langchain-community` | Page-by-page extraction |
| **WebBaseLoader** | Web pages | `langchain-community` | HTML parsing with BeautifulSoup |
| **TextLoader** | Plain text files | `langchain-community` | Simple text files |
| **JSONLoader** | JSON files/APIs | `langchain-community` | Extract specific JSON fields |
| **CSVLoader** | CSV files | `langchain-community` | Tabular data |
| **DirectoryLoader** | Multiple files | `langchain-community` | Bulk loading from directories |
| **UnstructuredLoader** | Various formats | `langchain-community` | PDFs, DOCXs, PPTs, images |

</loader-selection>

<when-to-choose-loader>
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
</when-to-choose-loader>

<ex-pdf>
Load PDF with lazy loading:

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
</ex-pdf>

<ex-web>
Web scraping with BeautifulSoup:

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
</ex-web>

<ex-text>
Simple text file loading:

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
</ex-text>

<ex-json>
JSON with jq extraction:

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
</ex-json>

<ex-csv>
CSV rows as documents:

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
</ex-csv>

<ex-directory>
Bulk load from directory:

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
</ex-directory>

<ex-unstructured>
Universal loader with OCR:

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
</ex-unstructured>

<ex-s3>
Load from S3 bucket:

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
</ex-s3>

<ex-metadata>
Enrich with custom metadata:

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
</ex-metadata>

<ex-lazy>
Stream large files:

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("large-file.pdf")

# Stream documents one at a time
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata.get('page', 0)}")
    # Process without loading all pages into memory
```
</ex-lazy>

<boundaries>
**What Agents CAN Do:**
- Load from various sources: PDF, text, CSV, JSON, DOCX, PPTX files, web pages, cloud storage (S3, GCS, Azure), APIs and databases
- Extract with metadata: Preserve source information, add custom metadata, track page numbers, URLs, timestamps
- Process efficiently: Use lazy loading for large files, batch process directories, stream data
- Customize extraction: Use jq for JSON extraction, BeautifulSoup for HTML parsing, OCR for scanned documents

**What Agents CANNOT Do:**
- Extract from encrypted/protected files: Cannot bypass password-protected PDFs, cannot access auth-required sites without credentials
- Process all formats automatically: Scanned PDFs need OCR, proprietary formats need specific loaders
- Bypass rate limits: Must respect website rate limiting
</boundaries>

<fix-import-community-package>
Updated import path:

```python
# OLD: Using langchain imports
from langchain.document_loaders import PyPDFLoader  # Deprecated!

# NEW: Use community package
from langchain_community.document_loaders import PyPDFLoader
```
</fix-import-community-package>

<fix-pypdf-vs-unstructured>
Use Unstructured for complex PDFs:

```python
# PyPDF may not work for complex PDFs
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("complex.pdf")
docs = loader.load()  # Poor extraction!

# Use Unstructured for complex PDFs
from langchain_community.document_loaders import UnstructuredPDFLoader
loader = UnstructuredPDFLoader("complex.pdf")
docs = loader.load()  # Better extraction
```
</fix-pypdf-vs-unstructured>

<fix-web-scraping-dependencies>
Install bs4 and lxml:

```python
# Missing dependencies
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
# ImportError: bs4 not found!

# Install required packages
# pip install beautifulsoup4 lxml
```
</fix-web-scraping-dependencies>

<fix-unstructured-api-keys>
Set API key or install dependencies:

```python
# Unstructured may need API key for advanced features
from langchain_community.document_loaders import UnstructuredFileLoader
loader = UnstructuredFileLoader("file.pdf", strategy="ocr_only")
# May fail without API key!

# Set API key or install dependencies
# pip install unstructured[local-inference]
# Or set UNSTRUCTURED_API_KEY environment variable
```
</fix-unstructured-api-keys>

<fix-encoding-issues>
Specify UTF-8 encoding:

```python
# Default encoding may fail
loader = TextLoader("file.txt")
docs = loader.load()  # UnicodeDecodeError!

# Specify encoding
loader = TextLoader("file.txt", encoding="utf-8")
docs = loader.load()
```
</fix-encoding-issues>

<fix-s3-credentials>
Configure AWS credentials:

```python
# Missing AWS credentials
from langchain_community.document_loaders import S3FileLoader
loader = S3FileLoader("bucket", "key")
docs = loader.load()  # Credential error!

# Configure AWS credentials
# Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# Or use AWS CLI: aws configure
```
</fix-s3-credentials>

<links>
- [LangChain Python Document Loaders](https://python.langchain.com/docs/integrations/document_loaders/)
- [PDF Loaders](https://python.langchain.com/docs/integrations/document_loaders/#pdfs)
- [Web Loaders](https://python.langchain.com/docs/integrations/document_loaders/#web)
</links>

<installation>
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
</installation>
