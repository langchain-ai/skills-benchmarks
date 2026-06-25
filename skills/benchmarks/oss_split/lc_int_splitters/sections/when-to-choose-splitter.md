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
