```python
from langsmith import Client

client = Client()

def run_agent(inputs: dict) -> dict:
    result = your_agent.invoke(inputs)
    return {"response": result}

results = await client.aevaluate(
    run_agent,
    data="Skills: Final Response",
    evaluators=[exact_match_evaluator, accuracy_evaluator, trajectory_evaluator],
    experiment_prefix="skills-eval-v1",
    max_concurrency=4
)
```
