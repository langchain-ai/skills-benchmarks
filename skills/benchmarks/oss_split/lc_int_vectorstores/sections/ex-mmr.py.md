Maximum marginal relevance for diverse results.

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = InMemoryVectorStore.from_texts(
    texts=["text1", "text2", "text3"],
    metadatas=[{}, {}, {}],
    embedding=OpenAIEmbeddings()
)

# MMR balances relevance and diversity
results = vectorstore.max_marginal_relevance_search(
    "query",
    k=3,
    fetch_k=10,  # Fetch 10 candidates, return 3 diverse results
    lambda_mult=0.5  # 0 = max diversity, 1 = max relevance
)
```
