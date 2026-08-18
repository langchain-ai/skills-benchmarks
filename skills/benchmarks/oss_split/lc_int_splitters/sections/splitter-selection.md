| Splitter | Best For | Package (Python / TypeScript) | Key Features |
|----------|----------|-------------------------------|--------------|
| **RecursiveCharacterTextSplitter** | General purpose | `langchain-text-splitters` / `@langchain/textsplitters` | Hierarchical splitting, preserves structure |
| **CharacterTextSplitter** | Simple splitting | `langchain-text-splitters` / `@langchain/textsplitters` | Split by single separator |
| **TokenTextSplitter** | Token-aware splitting | `langchain-text-splitters` / `@langchain/textsplitters` | Counts actual tokens, not characters |
| **MarkdownHeaderTextSplitter** | Markdown documents | `langchain-text-splitters` / `@langchain/textsplitters` | Preserves headers and structure |
| **SemanticChunker** | Semantic boundaries | `langchain-experimental` | AI-driven splitting (Python) |
| **RecursiveJsonSplitter** | JSON data | `langchain-text-splitters` / `@langchain/textsplitters` | Splits JSON while preserving structure |
