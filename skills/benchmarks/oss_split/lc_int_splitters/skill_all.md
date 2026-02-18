---
name: LangChain Text Splitters Integration
description: "[LangChain] Guide to using text splitter integrations in LangChain including recursive, character, and semantic splitters"
---

## Overview

Text splitters divide large documents into smaller chunks that fit within model context windows and enable effective retrieval. Proper chunking is critical for RAG system performance - chunks must be small enough for retrieval but large enough to preserve context.

### Key Concepts

- **Chunk Size**: Target size for each text chunk (in characters or tokens)
- **Chunk Overlap**: Number of characters/tokens to overlap between chunks (preserves context)
- **Separators**: Characters used to split text (newlines, periods, spaces)
- **Metadata**: Preserved and enriched during splitting (including start_index)

## Splitter Selection Decision Table

| Splitter | Best For | Package (Python / TypeScript) | Key Features |
|----------|----------|-------------------------------|--------------|
| **RecursiveCharacterTextSplitter** | General purpose | `langchain-text-splitters` / `@langchain/textsplitters` | Hierarchical splitting, preserves structure |
| **CharacterTextSplitter** | Simple splitting | `langchain-text-splitters` / `@langchain/textsplitters` | Split by single separator |
| **TokenTextSplitter** | Token-aware splitting | `langchain-text-splitters` / `@langchain/textsplitters` | Counts actual tokens, not characters |
| **MarkdownHeaderTextSplitter** | Markdown documents | `langchain-text-splitters` / `@langchain/textsplitters` | Preserves headers and structure |
| **SemanticChunker** | Semantic boundaries | `langchain-experimental` | AI-driven splitting (Python) |
| **RecursiveJsonSplitter** | JSON data | `langchain-text-splitters` / `@langchain/textsplitters` | Splits JSON while preserving structure |

### When to Choose Each Splitter

**Choose RecursiveCharacterTextSplitter if:**
- You're working with general text (default choice)
- You want to preserve natural text structure
- You need balanced chunks

**Choose TokenTextSplitter if:**
- You need precise token counts for model limits
- Character counts are unreliable for your use case

**Choose MarkdownHeaderTextSplitter if:**
- You're processing markdown documentation
- You want to preserve headers and structure

**Choose SemanticChunker if:**
- You want AI to determine boundaries
- Quality over speed

## Code Examples

### RecursiveCharacterTextSplitter (Recommended)

#### Python

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

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Basic usage
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,      // Target chunk size in characters
  chunkOverlap: 200,    // Overlap between chunks
});

const text = "Long document text here...";
const chunks = await splitter.splitText(text);

console.log(`Created ${chunks.length} chunks`);
chunks.forEach((chunk, i) => {
  console.log(`Chunk ${i + 1}: ${chunk.length} characters`);
});

// Split documents (preserves metadata)
import { Document } from "@langchain/core/documents";

const docs = [
  new Document({
    pageContent: "Long text...",
    metadata: { source: "doc1.pdf", page: 1 }
  })
];

const splitDocs = await splitter.splitDocuments(docs);
// Metadata is preserved and enriched with loc.lines
```

### How RecursiveCharacterTextSplitter Works (TypeScript)

```typescript
// Tries to split on these separators in order:
// 1. "\n\n" (double newline - paragraphs)
// 2. "\n" (single newline)
// 3. " " (space)
// 4. "" (character-by-character if needed)

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
  separators: ["\n\n", "\n", " ", ""], // Default, can customize
});

// This preserves natural text structure better than simple splitting
```

### CharacterTextSplitter

#### Python

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

#### TypeScript

```typescript
import { CharacterTextSplitter } from "@langchain/textsplitters";

// Split by single separator
const splitter = new CharacterTextSplitter({
  separator: "\n\n",    // Split on double newlines
  chunkSize: 1000,
  chunkOverlap: 200,
});

const chunks = await splitter.splitText(text);
```

### TokenTextSplitter (Token-Aware)

#### Python

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

#### TypeScript

```typescript
import { TokenTextSplitter } from "@langchain/textsplitters";

// Split based on actual token count
const splitter = new TokenTextSplitter({
  chunkSize: 512,       // Number of tokens, not characters
  chunkOverlap: 50,
  encodingName: "cl100k_base", // OpenAI's encoding
});

const chunks = await splitter.splitText(text);

// Good for precise model context window management
// 1 token ~ 4 characters for English text, but varies
```

### Markdown Splitter

#### Python

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

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Split markdown while preserving structure
const splitter = RecursiveCharacterTextSplitter.fromLanguage("markdown", {
  chunkSize: 1000,
  chunkOverlap: 200,
});

const markdown = `
# Header 1

Some content under header 1.

## Header 2

Content under header 2.
`;

const chunks = await splitter.splitText(markdown);
// Tries to keep headers with their content
```

### Code Splitter

#### Python

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

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Split code while preserving structure
const jsSplitter = RecursiveCharacterTextSplitter.fromLanguage("js", {
  chunkSize: 500,
  chunkOverlap: 50,
});

const pythonSplitter = RecursiveCharacterTextSplitter.fromLanguage("python", {
  chunkSize: 500,
  chunkOverlap: 50,
});

// Uses language-specific separators (functions, classes, etc.)
```

### Semantic Chunker (Python - Experimental)

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

### Custom Length Function (Python)

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

### Custom Separators (TypeScript)

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Custom splitting logic
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 100,
  separators: [
    "\n\n\n",  // Triple newline (section breaks)
    "\n\n",    // Double newline (paragraphs)
    "\n",      // Single newline
    ". ",      // Sentences
    " ",       // Words
    "",        // Characters
  ],
});
```

### Splitting Large PDFs

#### Python

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

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load PDF
const loader = new PDFLoader("large-document.pdf");
const docs = await loader.load();

// Split into manageable chunks
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});

const splitDocs = await splitter.splitDocuments(docs);

console.log(`${docs.length} pages split into ${splitDocs.length} chunks`);

// Each chunk preserves source metadata
splitDocs.forEach(chunk => {
  console.log(chunk.metadata); // Includes original page number
});
```

### Splitting with Vector Store Integration

#### Python

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

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

// Complete RAG pipeline
const loader = new CheerioWebBaseLoader("https://docs.example.com");
const docs = await loader.load();

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});

const splitDocs = await splitter.splitDocuments(docs);

const vectorStore = await MemoryVectorStore.fromDocuments(
  splitDocs,
  new OpenAIEmbeddings()
);

// Now ready for semantic search
const results = await vectorStore.similaritySearch("query", 4);
```

## Boundaries

### What Agents CAN Do

- **Split text intelligently** - Use recursive splitting to preserve structure, configure chunk size and overlap, choose appropriate separators
- **Handle various formats** - Plain text, markdown, code, documents with metadata, JSON and structured data
- **Optimize for use case** - Balance chunk size vs context, adjust overlap for continuity, use token-based splitting for models
- **Integrate with pipelines** - Combine with loaders and vector stores, preserve metadata through splitting

### What Agents CANNOT Do

- **Guarantee semantic boundaries** - Splitters use heuristics, not perfect semantic understanding; may split mid-sentence in edge cases
- **Perfectly estimate tokens** - Character-based splitters approximate tokens; use TokenTextSplitter for exact counts
- **Split without losing some context** - Even with overlap, some context may be lost; trade-off between chunk size and context

## Gotchas

### 1. Chunk Size vs Token Limits

#### Python

```python
# ❌ Character count != token count
splitter = RecursiveCharacterTextSplitter(chunk_size=4000)
# May exceed 4096 token limit!

# ✅ Use token-aware splitter
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=4000)
```

#### TypeScript

```typescript
// ❌ Character count != token count
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 4000,  // Characters
});
// GPT-3.5 has 4096 token limit, this may exceed it!

// ✅ Use TokenTextSplitter for precise token counts
import { TokenTextSplitter } from "@langchain/textsplitters";

const splitter = new TokenTextSplitter({
  chunkSize: 4000,  // Actual tokens
  encodingName: "cl100k_base",
});
```

**Fix**: Use TokenTextSplitter when token precision matters.

### 2. Import from Correct Package (Python)

```python
# ❌ OLD
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ NEW
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

**Fix**: Use `langchain-text-splitters` package.

### 3. Too Small Chunks Lose Context (TypeScript)

```typescript
// ❌ Chunks too small
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 100,    // Very small
  chunkOverlap: 0,   // No overlap
});
// Chunks lack sufficient context for good retrieval

// ✅ Reasonable chunk size with overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,   // Good size
  chunkOverlap: 200, // 20% overlap
});
```

**Fix**: Use 500-2000 characters with 10-20% overlap for most cases.

### 4. Zero Overlap Breaks Continuity

#### Python

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

#### TypeScript

```typescript
// ❌ No overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 0,  // Information at boundaries may be lost
});

// ✅ Use overlap to preserve context
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,  // 20% overlap is good default
});
```

**Fix**: Always use overlap (typically 10-20% of chunk size).

### 5. Metadata Not Preserved

#### Python

```python
# ❌ split_text loses metadata
chunks = splitter.split_text(text)

# ✅ Use split_documents
docs = [Document(page_content=text, metadata={"source": "file"})]
chunks = splitter.split_documents(docs)
```

#### TypeScript

```typescript
// ❌ Using splitText loses metadata
const chunks = await splitter.splitText(documentText);
// No metadata!

// ✅ Use splitDocuments to preserve metadata
const docs = [new Document({
  pageContent: documentText,
  metadata: { source: "file.pdf" }
})];
const chunks = await splitter.splitDocuments(docs);
// Metadata preserved!
```

**Fix**: Use `split_documents()`/`splitDocuments()` instead of `split_text()`/`splitText()` to keep metadata.

## Links to Documentation

### Python
- [LangChain Python Text Splitters](https://python.langchain.com/docs/integrations/text_splitters/)

### TypeScript
- [LangChain JS Text Splitters](https://js.langchain.com/docs/integrations/text_splitters/)
- [RecursiveCharacterTextSplitter](https://js.langchain.com/docs/modules/data_connection/document_transformers/)

### Package Installation

**Python:**
```bash
pip install langchain-text-splitters

# For semantic chunker
pip install langchain-experimental
```

**TypeScript:**
```bash
npm install @langchain/textsplitters
```
