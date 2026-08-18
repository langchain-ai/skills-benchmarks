Language-aware code splitting:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# Python code splitter
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
)

python_code = """
def function1():
    pass

class MyClass:
    def method1(self):
        pass
"""

chunks = python_splitter.split_text(python_code)

# JavaScript splitter
js_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size=500,
    chunk_overlap=50,
)
```
