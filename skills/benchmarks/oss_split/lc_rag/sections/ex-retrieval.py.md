Similarity search and MMR retrieval:

```python
# Similarity search with scores
results = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results:
    print(f"Score: {score}, Content: {doc.page_content}")

# MMR (Maximum Marginal Relevance) for diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```
