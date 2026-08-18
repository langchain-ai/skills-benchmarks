Question/chunks/answer - tests retrieval quality. Only matches runs with `run_type="retriever"`.

```python
import json
from pathlib import Path

examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    retrievers = [r for r in runs if r.get("run_type") == "retriever"]

    if not root or not retrievers:
        continue

    for ret in retrievers:
        chunks = ret.get("outputs", {})
        # Extract page_content from LangChain Documents if present
        if isinstance(chunks, dict) and "documents" in chunks:
            chunks = [d.get("page_content", str(d)) for d in chunks["documents"]]

        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": {"question": root["inputs"].get("query", "")},
            "outputs": {
                "answer": root.get("outputs", {}).get("output", ""),
                "retrieved_chunks": chunks,
            }
        })

with open("/tmp/rag_dataset.json", "w") as f:
    json.dump(examples, f, indent=2)
```

**Structure:**
```json
{
  "trace_id": "...",
  "inputs": {"question": "How do I..."},
  "outputs": {
    "answer": "The answer is...",
    "retrieved_chunks": ["Chunk 1", "Chunk 2"]
  }
}
```

For custom retriever names, filter by `name` instead of `run_type`.
