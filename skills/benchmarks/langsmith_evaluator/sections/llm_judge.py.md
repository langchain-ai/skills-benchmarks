Use structured output for reliable grading:

```python
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI

class AccuracyGrade(TypedDict):
    reasoning: Annotated[str, ..., "Explain your reasoning"]
    is_accurate: Annotated[bool, ..., "True if response is accurate"]
    confidence: Annotated[float, ..., "Confidence 0.0-1.0"]

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(
    AccuracyGrade, method="json_schema", strict=True
)

async def accuracy_evaluator(run, example):
    expected = example["outputs"].get('response', '')
    agent_output = run["outputs"].get('response', '')

    prompt = f"""Expected: {expected}
Agent Output: {agent_output}
Evaluate accuracy:"""

    grade = await judge.ainvoke([{"role": "user", "content": prompt}])

    return {
        "accuracy": 1 if grade["is_accurate"] else 0,
        "comment": f"{grade['reasoning']} (confidence: {grade['confidence']})"
    }
```
