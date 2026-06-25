Enable Chroma disk persistence.

```python
# Not persisting
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings()
)  # Ephemeral!

# Persist to disk
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)
```
