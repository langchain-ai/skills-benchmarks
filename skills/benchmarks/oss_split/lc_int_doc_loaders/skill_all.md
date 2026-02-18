---
name: LangChain Document Loaders Integration
description: "[LangChain] Guide to using document loader integrations in LangChain for PDFs, web pages, text files, and APIs"
---

<oneliner>
Document loaders extract data from various sources and formats into LangChain's standardized Document format, essential for building RAG systems.
</oneliner>

<overview>
Key Concepts:
- **Document**: Object with `page_content`/`pageContent` (text) and `metadata` (source info, page numbers, etc.)
- **Loaders**: Classes that extract content from specific sources/formats
- **Metadata**: Contextual information preserved during loading (URLs, file paths, page numbers)
- **Lazy Loading**: Stream documents without loading everything into memory
</overview>

<loader-selection>
| Loader Type | Best For | Package (Python / TypeScript) | Key Features |
|-------------|----------|-------------------------------|--------------|
| **PDF Loader** | PDF files | `langchain-community` / `@langchain/community` | Page-by-page extraction |
| **Web Loader** | Web pages | `langchain-community` / `@langchain/community` | HTML parsing |
| **Text Loader** | Plain text files | `langchain-community` / `langchain` | Simple text files |
| **JSON Loader** | JSON files/APIs | `langchain-community` / `langchain` | Extract specific JSON fields |
| **CSV Loader** | CSV files | `langchain-community` / `@langchain/community` | Tabular data |
| **Directory Loader** | Multiple files | `langchain-community` / `langchain` | Bulk loading from directories |
</loader-selection>

<when-to-choose-loader>
**Choose PDF Loader if:**
- You're processing standard PDF documents
- You need page number metadata
- PDFs contain extractable text

**Choose Web Loader if:**
- You're scraping web pages
- You need to parse HTML content
- You want to filter by CSS selectors

**Choose Unstructured Loader (Python) if:**
- You have mixed document types
- You need OCR for scanned documents
- You want sophisticated parsing
</when-to-choose-loader>

<ex-pdf>
<python>
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

</python>

<typescript>
PDF with page metadata:

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load PDF file
const loader = new PDFLoader("path/to/document.pdf");
const docs = await loader.load();

console.log(`Loaded ${docs.length} pages`);
docs.forEach((doc, i) => {
  console.log(`Page ${i + 1}:`, doc.metadata);
  console.log(doc.pageContent.substring(0, 100));
});

// Each page is a separate document
// metadata includes: source, pdf.totalPages, loc.pageNumber
```

</typescript>
</ex-pdf>

<ex-web>
<python>
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

</python>

<typescript>
Cheerio for static pages:

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

// Load single URL
const loader = new CheerioWebBaseLoader(
  "https://docs.langchain.com"
);

const docs = await loader.load();
console.log(docs[0].pageContent);
console.log(docs[0].metadata); // { source: url, ... }

// With custom selector
const loaderWithSelector = new CheerioWebBaseLoader(
  "https://news.ycombinator.com",
  {
    selector: ".storylink",  // Only extract specific elements
  }
);

// Multiple URLs
const loaderMultiple = new CheerioWebBaseLoader([
  "https://example.com/page1",
  "https://example.com/page2",
]);
const allDocs = await loaderMultiple.load();
```

</typescript>

<typescript>
Playwright for JS-rendered pages:

```typescript
import { PlaywrightWebBaseLoader } from "@langchain/community/document_loaders/web/playwright";

// For JavaScript-rendered pages
const loader = new PlaywrightWebBaseLoader("https://spa-app.com", {
  launchOptions: {
    headless: true,
  },
  gotoOptions: {
    waitUntil: "networkidle",  // Wait for JS to finish
  },
  evaluateOptions: {
    // Custom evaluation function
    evaluate: (page) => page.evaluate(() => document.body.innerText),
  },
});

const docs = await loader.load();
```

</typescript>
</ex-web>

<ex-text>
<python>
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

</python>

<typescript>
Text file with metadata:

```typescript
import { TextLoader } from "langchain/document_loaders/fs/text";

const loader = new TextLoader("path/to/file.txt");
const docs = await loader.load();

// Returns single document with entire file content
console.log(docs[0].pageContent);
console.log(docs[0].metadata.source); // File path
```

</typescript>
</ex-text>

<ex-json>
<python>
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

</python>

<typescript>
JSON with JSONPointer extraction:

```typescript
import { JSONLoader } from "langchain/document_loaders/fs/json";

// Load JSON with specific field extraction
const loader = new JSONLoader(
  "path/to/data.json",
  ["/texts/*/content"]  // JSONPointer to extract specific fields
);

const docs = await loader.load();

// Example JSON: { "texts": [{ "content": "...", "id": 1 }] }
// Each matching field becomes a document
```

</typescript>
</ex-json>

<ex-csv>
<python>
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

</python>

<typescript>
CSV with column config:

```typescript
import { CSVLoader } from "@langchain/community/document_loaders/fs/csv";

const loader = new CSVLoader("path/to/data.csv", {
  column: "text",  // Column to use as page_content
  separator: ",",
});

const docs = await loader.load();

// Each row becomes a document
// Other columns stored in metadata
```

</typescript>
</ex-csv>

<ex-directory>
<python>
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

</python>

<typescript>
Multi-format directory loader:

```typescript
import { DirectoryLoader } from "langchain/document_loaders/fs/directory";
import { TextLoader } from "langchain/document_loaders/fs/text";
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load all files from directory
const loader = new DirectoryLoader(
  "path/to/documents",
  {
    ".txt": (path) => new TextLoader(path),
    ".pdf": (path) => new PDFLoader(path),
  }
);

const docs = await loader.load();
console.log(`Loaded ${docs.length} documents from directory`);
```

</typescript>
</ex-directory>

<ex-unstructured>
<python>
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
</python>
</ex-unstructured>

<ex-s3>
<python>
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
</python>
</ex-s3>

<ex-github>
<typescript>
Load GitHub repository:

```typescript
import { GithubRepoLoader } from "@langchain/community/document_loaders/web/github";

const loader = new GithubRepoLoader(
  "https://github.com/langchain-ai/langchainjs",
  {
    branch: "main",
    recursive: true,
    ignorePaths: ["node_modules/**", "dist/**"],
    maxConcurrency: 5,
  }
);

const docs = await loader.load();
// Each file becomes a document
```
</typescript>
</ex-github>

<ex-metadata>
<python>
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

</python>

<typescript>
Add timestamp and category:

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://blog.com/post");
const docs = await loader.load();

// Add custom metadata
const enrichedDocs = docs.map(doc => ({
  ...doc,
  metadata: {
    ...doc.metadata,
    loadedAt: new Date().toISOString(),
    category: "blog",
  },
}));
```

</typescript>
</ex-metadata>

<ex-lazy>
<python>
Stream large files:

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("large-file.pdf")

# Stream documents one at a time
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata.get('page', 0)}")
    # Process without loading all pages into memory
```

</python>

<typescript>
Memory-efficient streaming:

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("large-file.pdf");

// Use lazy() for large files - streams documents
for await (const doc of loader.lazy()) {
  console.log("Processing page:", doc.metadata.loc.pageNumber);
  // Process one page at a time without loading all into memory
}
```

</typescript>
</ex-lazy>

<boundaries>
What You CAN Do:
- **Load from various sources** - PDF, text, CSV, JSON, DOCX files, web pages, cloud storage
- **Extract with metadata** - Preserve source information, add custom metadata
- **Process efficiently** - Use lazy loading for large files, batch process directories
- **Customize extraction** - Use jq/JSONPointer for JSON, CSS selectors for HTML

What You CANNOT Do:
- **Extract from encrypted/protected files** - Cannot bypass password-protected PDFs
- **Process all formats automatically** - Scanned PDFs need OCR, proprietary formats need specific loaders
- **Bypass rate limits** - Must respect website rate limiting
</boundaries>

<fix-import-community-package>
<python>
Updated import path:

```python
# OLD: Using langchain imports
from langchain.document_loaders import PyPDFLoader  # Deprecated!

# NEW: Use community package
from langchain_community.document_loaders import PyPDFLoader
```
</python>
</fix-import-community-package>

<fix-pdf-loader-dependencies>
<python>
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
</python>

<typescript>
Install pdf-parse dependency:

```typescript
// Will fail if pdf-parse not installed
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
const loader = new PDFLoader("file.pdf");

// Install dependencies first
// npm install pdf-parse

const loader = new PDFLoader("file.pdf");
const docs = await loader.load(); // Works!
```
</typescript>
</fix-pdf-loader-dependencies>

<fix-web-scraping-dependencies>
<python>
Install bs4 and lxml:

```python
# Missing dependencies
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
# ImportError: bs4 not found!

# Install required packages
# pip install beautifulsoup4 lxml
```
</python>
</fix-web-scraping-dependencies>

<fix-cheerio-vs-playwright>
<typescript>
Use Playwright for SPAs:

```typescript
// Using Cheerio for dynamic content
const loader = new CheerioWebBaseLoader("https://react-app.com");
const docs = await loader.load();
// Content is empty or incomplete!

// Use Playwright for JavaScript-rendered pages
const loader = new PlaywrightWebBaseLoader("https://react-app.com", {
  gotoOptions: { waitUntil: "networkidle" }
});
```
</typescript>
</fix-cheerio-vs-playwright>

<fix-encoding-issues>
<python>
Specify UTF-8 encoding:

```python
# Default encoding may fail
loader = TextLoader("file.txt")
docs = loader.load()  # UnicodeDecodeError!

# Specify encoding
loader = TextLoader("file.txt", encoding="utf-8")
docs = loader.load()
```
</python>
</fix-encoding-issues>

<fix-json-pointer-syntax>
<typescript>
JSONPointer starts with /:

```typescript
// Wrong JSON pointer format
const loader = new JSONLoader("data.json", ["texts.content"]);

// Correct JSON pointer format (starts with /)
const loader = new JSONLoader("data.json", ["/texts/0/content"]);
```
</typescript>
</fix-json-pointer-syntax>

<fix-directory-loader-extensions>
<typescript>
Include dot in extensions:

```typescript
// Extensions don't match
const loader = new DirectoryLoader("docs", {
  "txt": (path) => new TextLoader(path),  // Wrong!
});

// Include the dot
const loader = new DirectoryLoader("docs", {
  ".txt": (path) => new TextLoader(path),
  ".pdf": (path) => new PDFLoader(path),
});
```
</typescript>
</fix-directory-loader-extensions>

<fix-large-files-memory>
<python>
Use lazy loading:

```python
# Loading huge PDF into memory
loader = PyPDFLoader("huge-book.pdf")
docs = loader.load()  # May crash!

# Use lazy loading
for doc in loader.lazy_load():
    process_document(doc)
```
</python>

<typescript>
Stream instead of load all:

```typescript
// Loading huge PDF into memory
const loader = new PDFLoader("huge-book.pdf");
const docs = await loader.load(); // May crash!

// Use lazy loading
for await (const doc of loader.lazy()) {
  processDocument(doc);
  // Only one page in memory at a time
}
```
</typescript>
</fix-large-files-memory>

<links>
Python:
- [Document Loaders Overview](https://python.langchain.com/docs/integrations/document_loaders/)
- [PDF Loaders](https://python.langchain.com/docs/integrations/document_loaders/#pdfs)
- [Web Loaders](https://python.langchain.com/docs/integrations/document_loaders/#web)

TypeScript:
- [Document Loaders Overview](https://js.langchain.com/docs/integrations/document_loaders/)
- [PDF Loader](https://js.langchain.com/docs/integrations/document_loaders/file_loaders/pdf)
- [Web Loaders](https://js.langchain.com/docs/integrations/document_loaders/web_loaders/)
</links>

<installation>
Python:

```bash
pip install langchain-community pypdf beautifulsoup4 lxml unstructured
```

TypeScript:

```bash
npm install @langchain/community pdf-parse playwright
npx playwright install
```
</installation>
