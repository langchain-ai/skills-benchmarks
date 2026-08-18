Use MMR (Maximal Marginal Relevance) to balance relevance and diversity in search results.
```python
# MMR balances relevance and diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```
