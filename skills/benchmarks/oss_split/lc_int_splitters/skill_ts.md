---
name: LangChain Text Splitters Integration (TypeScript)
description: [LangChain] Guide to using text splitter integrations in LangChain including recursive, character, and semantic splitters
---

<overview>
Text splitters divide large documents into smaller chunks that fit within model context windows and enable effective retrieval. Proper chunking is critical for RAG system performance - chunks must be small enough for retrieval but large enough to preserve context.

**Key Concepts:**
- **Chunk Size**: Target size for each text chunk (in characters or tokens)
- **Chunk Overlap**: Number of characters/tokens to overlap between chunks (preserves context)
- **Separators**: Characters used to split text (newlines, periods, spaces)
- **Metadata**: Preserved and enriched during splitting (including start_index)
</overview>

<splitter-selection>
| Splitter | Best For | Package | Key Features |
|----------|----------|---------|--------------|
| **RecursiveCharacterTextSplitter** | General purpose | `@langchain/textsplitters` | Hierarchical splitting, preserves structure |
| **CharacterTextSplitter** | Simple splitting | `@langchain/textsplitters` | Split by single separator |
| **TokenTextSplitter** | Token-aware splitting | `@langchain/textsplitters` | Counts actual tokens, not characters |
| **MarkdownTextSplitter** | Markdown documents | `@langchain/textsplitters` | Preserves markdown structure |
| **RecursiveJsonSplitter** | JSON data | `@langchain/textsplitters` | Splits JSON while preserving structure |
</splitter-selection>

<when-to-choose>
**Choose RecursiveCharacterTextSplitter if:**
- You're working with general text (default choice)
- You want to preserve natural text structure
- You need balanced chunks

**Choose TokenTextSplitter if:**
- You need precise token counts for model limits
- Character counts are unreliable for your use case

**Choose MarkdownTextSplitter if:**
- You're processing markdown documentation
- You want to preserve headers and structure
</when-to-choose>

<ex-recursive-character-text-splitter>
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
</ex-recursive-character-text-splitter>

<ex-how-recursive-splitter-works>
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
</ex-how-recursive-splitter-works>

<ex-character-text-splitter>
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
</ex-character-text-splitter>

<ex-token-text-splitter>
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
// 1 token ≈ 4 characters for English text, but varies
```
</ex-token-text-splitter>

<ex-markdown-text-splitter>
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
</ex-markdown-text-splitter>

<ex-splitting-long-documents>
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
</ex-splitting-long-documents>

<ex-code-splitting>
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
</ex-code-splitting>

<ex-custom-separators>
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
</ex-custom-separators>

<ex-splitting-with-vector-store-integration>
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
</ex-splitting-with-vector-store-integration>

<boundaries>
**What Agents CAN Do:**
- Split text intelligently using recursive splitting to preserve structure
- Configure chunk size and overlap
- Choose appropriate separators
- Handle various formats (plain text, markdown, code, documents with metadata, JSON)
- Optimize for use case by balancing chunk size vs context
- Integrate with pipelines combining loaders and vector stores

**What Agents CANNOT Do:**
- Guarantee semantic boundaries (splitters use heuristics, not perfect semantic understanding)
- Perfectly estimate tokens (character-based splitters approximate tokens)
- Split without losing some context (trade-off between chunk size and context)
</boundaries>

<fix-chunk-size-vs-token-limits>
```typescript
// WRONG: Character count != token count
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 4000,  // Characters
});
// GPT-3.5 has 4096 token limit, this may exceed it!

// CORRECT: Use TokenTextSplitter for precise token counts
import { TokenTextSplitter } from "@langchain/textsplitters";

const splitter = new TokenTextSplitter({
  chunkSize: 4000,  // Actual tokens
  encodingName: "cl100k_base",
});
```

**Fix**: Use TokenTextSplitter when token precision matters.
</fix-chunk-size-vs-token-limits>

<fix-too-small-chunks-lose-context>
```typescript
// WRONG: Chunks too small
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 100,    // Very small
  chunkOverlap: 0,   // No overlap
});
// Chunks lack sufficient context for good retrieval

// CORRECT: Reasonable chunk size with overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,   // Good size
  chunkOverlap: 200, // 20% overlap
});
```

**Fix**: Use 500-2000 characters with 10-20% overlap for most cases.
</fix-too-small-chunks-lose-context>

<fix-zero-overlap-breaks-continuity>
```typescript
// WRONG: No overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 0,  // Information at boundaries may be lost
});

// CORRECT: Use overlap to preserve context
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,  // 20% overlap is good default
});
```

**Fix**: Always use overlap (typically 10-20% of chunk size).
</fix-zero-overlap-breaks-continuity>

<fix-metadata-not-preserved>
```typescript
// WRONG: Using splitText loses metadata
const chunks = await splitter.splitText(documentText);
// No metadata!

// CORRECT: Use splitDocuments to preserve metadata
const docs = [new Document({
  pageContent: documentText,
  metadata: { source: "file.pdf" }
})];
const chunks = await splitter.splitDocuments(docs);
// Metadata preserved!
```

**Fix**: Use `splitDocuments()` instead of `splitText()` to keep metadata.
</fix-metadata-not-preserved>

<documentation-links>
- [LangChain JS Text Splitters](https://js.langchain.com/docs/integrations/text_splitters/)
- [RecursiveCharacterTextSplitter](https://js.langchain.com/docs/modules/data_connection/document_transformers/)

**Package Installation:**
```bash
npm install @langchain/textsplitters
```
</documentation-links>
