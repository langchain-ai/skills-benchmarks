For non-LangChain apps, use the `@traceable` decorator and wrap your LLM client:

```python
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())

@traceable
def my_llm_pipeline(question: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content

# Nested tracing example
@traceable
def rag_pipeline(question: str) -> str:
    docs = retrieve_docs(question)
    return generate_answer(question, docs)

@traceable(name="retrieve_docs")
def retrieve_docs(query: str) -> list[str]:
    return docs

@traceable(name="generate_answer")
def generate_answer(question: str, docs: list[str]) -> str:
    return client.chat.completions.create(...)
```

Best Practices:
- **Apply `@traceable` to all nested functions** you want visible in LangSmith
- **Wrapped clients auto-trace all calls** — `wrap_openai()` records every LLM call
- **Name your traces** for easier filtering: `@traceable(name="retrieve_docs")`
- **Add metadata** for searchability: `@traceable(metadata={"user_id": "123"})`
