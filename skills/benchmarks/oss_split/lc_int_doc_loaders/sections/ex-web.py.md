Web scraping with BeautifulSoup:

```python
from langchain_community.document_loaders import WebBaseLoader

# Load single URL
loader = WebBaseLoader("https://docs.langchain.com")
docs = loader.load()

print(docs[0].page_content)
print(docs[0].metadata)  # {'source': url, ...}

# With custom BeautifulSoup parsing
loader = WebBaseLoader(
    "https://news.ycombinator.com",
    bs_kwargs={
        "parse_only": bs4.SoupStrainer(class_=("storylink", "subtext"))
    }
)

# Multiple URLs
loader = WebBaseLoader([
    "https://example.com/page1",
    "https://example.com/page2",
])
docs = loader.load()
```
