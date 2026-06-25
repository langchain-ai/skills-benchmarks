Handle HuggingFace model download on first run.

```python
# First run may be slow (downloading model)
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
# Downloads ~420MB on first run!

# Be aware and cache models
# Models are cached in ~/.cache/huggingface/
# Subsequent runs will be fast
```
