AI-driven semantic chunking:

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
