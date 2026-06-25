Install bs4 and lxml:

```python
# Missing dependencies
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
# ImportError: bs4 not found!

# Install required packages
# pip install beautifulsoup4 lxml
```
