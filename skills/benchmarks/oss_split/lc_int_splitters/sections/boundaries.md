What You CAN Do:
- **Split text intelligently** - Use recursive splitting to preserve structure, configure chunk size and overlap, choose appropriate separators
- **Handle various formats** - Plain text, markdown, code, documents with metadata, JSON and structured data
- **Optimize for use case** - Balance chunk size vs context, adjust overlap for continuity, use token-based splitting for models
- **Integrate with pipelines** - Combine with loaders and vector stores, preserve metadata through splitting

What You CANNOT Do:
- **Guarantee semantic boundaries** - Splitters use heuristics, not perfect semantic understanding; may split mid-sentence in edge cases
- **Perfectly estimate tokens** - Character-based splitters approximate tokens; use TokenTextSplitter for exact counts
- **Split without losing some context** - Even with overlap, some context may be lost; trade-off between chunk size and context
