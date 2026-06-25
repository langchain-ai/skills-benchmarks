Query Wikipedia for encyclopedic information.

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000,
    )
)

# Query Wikipedia
result = wikipedia.invoke("Artificial Intelligence")
print(result)
```
