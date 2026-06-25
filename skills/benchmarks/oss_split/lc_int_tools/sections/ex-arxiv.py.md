Search academic papers on ArXiv.

```python
from langchain_community.tools import ArxivQueryRun

arxiv_tool = ArxivQueryRun()

# Search academic papers
results = arxiv_tool.invoke("large language models")
print(results)
```
