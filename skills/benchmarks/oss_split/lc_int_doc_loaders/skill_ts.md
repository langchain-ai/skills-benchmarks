---
name: LangChain Document Loaders Integration (TypeScript)
description: [LangChain] Guide to using document loader integrations in LangChain for PDFs, web pages, text files, and APIs
---

# langchain-document-loaders (JavaScript/TypeScript)

## Overview

Document loaders extract data from various sources and formats into LangChain's standardized Document format. They're essential for building RAG systems, as they convert raw data into processable text chunks with metadata.

### Key Concepts

- **Document**: Object with `pageContent` (text) and `metadata` (source info, page numbers, etc.)
- **Loaders**: Classes that extract content from specific sources/formats
- **Metadata**: Contextual information preserved during loading (URLs, file paths, page numbers)
- **Lazy Loading**: Stream documents without loading everything into memory

## Loader Selection Decision Table

| Loader Type | Best For | Package | Key Features |
|-------------|----------|---------|--------------|
| **PDFLoader** | PDF files | `@langchain/community` | Extracts text and page numbers |
| **CheerioWebBaseLoader** | Web pages (static) | `@langchain/community` | HTML parsing with Cheerio |
| **PlaywrightWebBaseLoader** | Web pages (dynamic) | `@langchain/community` | JavaScript-rendered content |
| **TextLoader** | Plain text files | `langchain/document_loaders/fs/text` | Simple text files |
| **JSONLoader** | JSON files/APIs | `langchain/document_loaders/fs/json` | Extract specific JSON fields |
| **CSVLoader** | CSV files | `@langchain/community` | Tabular data |
| **DirectoryLoader** | Multiple files | `langchain/document_loaders/fs/directory` | Bulk loading from directories |
| **GithubRepoLoader** | GitHub repos | `@langchain/community` | Clone and load repo files |
| **NotionLoader** | Notion pages | `@langchain/community` | Notion workspace data |

### When to Choose Each Loader

**Choose PDFLoader if:**
- You're processing PDF documents
- You need page number metadata
- PDFs contain extractable text (not just images)

**Choose CheerioWebBaseLoader if:**
- You're scraping static web pages
- Content doesn't require JavaScript
- You want fast, lightweight scraping

**Choose PlaywrightWebBaseLoader if:**
- Web pages require JavaScript to render
- You need to interact with dynamic content
- You're dealing with SPAs or React apps

**Choose TextLoader if:**
- You have simple plain text files
- No special parsing needed
- Direct file-to-document conversion

## Code Examples

### PDF Loader

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

### Web Scraping - Cheerio (Static)

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

### Web Scraping - Playwright (Dynamic)

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

### Text File Loader

```typescript
import { TextLoader } from "langchain/document_loaders/fs/text";

const loader = new TextLoader("path/to/file.txt");
const docs = await loader.load();

// Returns single document with entire file content
console.log(docs[0].pageContent);
console.log(docs[0].metadata.source); // File path
```

### JSON Loader

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

### CSV Loader

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

### Directory Loader

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

### GitHub Loader

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

### Custom Metadata Example

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

### Lazy Loading (Memory Efficient)

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("large-file.pdf");

// Use lazy() for large files - streams documents
for await (const doc of loader.lazy()) {
  console.log("Processing page:", doc.metadata.loc.pageNumber);
  // Process one page at a time without loading all into memory
}
```

## Boundaries

### What Agents CAN Do

✅ **Load from various sources**
- PDF, text, CSV, JSON files
- Web pages (static and dynamic)
- GitHub repositories, Notion pages
- APIs and custom sources

✅ **Extract with metadata**
- Preserve source information
- Add custom metadata fields
- Track page numbers, URLs, file paths

✅ **Process efficiently**
- Use lazy loading for large files
- Batch process directories
- Stream data without loading everything

✅ **Customize extraction**
- Use CSS selectors for web scraping
- Extract specific JSON fields
- Filter and transform content

### What Agents CANNOT Do

❌ **Extract from encrypted/protected files**
- Cannot bypass password-protected PDFs
- Cannot access authentication-required websites without credentials

❌ **Process binary data directly**
- Cannot extract from images without OCR
- Cannot process proprietary formats without converters

❌ **Handle all PDF types**
- Scanned PDFs need OCR
- Image-based PDFs won't extract text

❌ **Bypass rate limits**
- Cannot ignore website rate limiting
- Must respect robots.txt

## Gotchas

### 1. **PDF Loader Requires Installation**

```typescript
// ❌ Will fail if pdf-parse not installed
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
const loader = new PDFLoader("file.pdf");

// ✅ Install dependencies first
// npm install pdf-parse

const loader = new PDFLoader("file.pdf");
const docs = await loader.load(); // Works!
```

**Fix**: Install required peer dependencies: `npm install pdf-parse`

### 2. **Web Scraping Blocked by CORS/Robots**

```typescript
// ❌ May fail due to CORS or blocking
const loader = new CheerioWebBaseLoader("https://protected-site.com");
await loader.load(); // Error!

// ✅ Check robots.txt and use appropriate loader
// For client-side blocking, run in Node.js (server-side)
// For dynamic content, use Playwright

const loader = new PlaywrightWebBaseLoader("https://protected-site.com");
```

**Fix**: Use PlaywrightWebBaseLoader for blocked sites or check robots.txt.

### 3. **Large Files and Memory**

```typescript
// ❌ Loading huge PDF into memory
const loader = new PDFLoader("huge-book.pdf");
const docs = await loader.load(); // May crash!

// ✅ Use lazy loading
for await (const doc of loader.lazy()) {
  processDocument(doc);
  // Only one page in memory at a time
}
```

**Fix**: Use `lazy()` method for large files.

### 4. **Path Resolution Issues**

```typescript
// ❌ Relative paths may not work as expected
const loader = new TextLoader("./data/file.txt");

// ✅ Use absolute paths or path module
import path from "path";
const filePath = path.join(process.cwd(), "data", "file.txt");
const loader = new TextLoader(filePath);
```

**Fix**: Use absolute paths or `path` module for reliability.

### 5. **Cheerio vs Playwright Confusion**

```typescript
// ❌ Using Cheerio for dynamic content
const loader = new CheerioWebBaseLoader("https://react-app.com");
const docs = await loader.load();
// Content is empty or incomplete!

// ✅ Use Playwright for JavaScript-rendered pages
const loader = new PlaywrightWebBaseLoader("https://react-app.com", {
  gotoOptions: { waitUntil: "networkidle" }
});
```

**Fix**: Use Playwright for SPAs and dynamic content.

### 6. **JSON Pointer Syntax**

```typescript
// ❌ Wrong JSON pointer format
const loader = new JSONLoader("data.json", ["texts.content"]);

// ✅ Correct JSON pointer format (starts with /)
const loader = new JSONLoader("data.json", ["/texts/0/content"]);
```

**Fix**: JSON pointers must start with `/` and use `/` as separator.

### 7. **Directory Loader File Extension Matching**

```typescript
// ❌ Extensions don't match
const loader = new DirectoryLoader("docs", {
  "txt": (path) => new TextLoader(path),  // Wrong!
});

// ✅ Include the dot
const loader = new DirectoryLoader("docs", {
  ".txt": (path) => new TextLoader(path),
  ".pdf": (path) => new PDFLoader(path),
});
```

**Fix**: File extensions must include the dot (`.txt`, `.pdf`).

## Links and Resources

### Official Documentation
- [LangChain JS Document Loaders](https://js.langchain.com/docs/integrations/document_loaders/)
- [PDF Loader](https://js.langchain.com/docs/integrations/document_loaders/file_loaders/pdf)
- [Web Loaders](https://js.langchain.com/docs/integrations/document_loaders/web_loaders/)
- [File System Loaders](https://js.langchain.com/docs/integrations/document_loaders/file_loaders/)

### Package Installation
```bash
# Community loaders
npm install @langchain/community

# PDF support
npm install pdf-parse

# Playwright for dynamic web pages
npm install playwright
npx playwright install
```
