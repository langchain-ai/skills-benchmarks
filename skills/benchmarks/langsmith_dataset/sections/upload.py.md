```bash
# Upload local JSON file as a dataset
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory"

# Create empty dataset and add examples individually
langsmith dataset create --name "Skills: Final Response"
langsmith example create --dataset "Skills: Final Response" \
  --inputs '{"query": "test"}' \
  --outputs '{"answer": "result"}'
```

Or upload using the SDK:

```python
from langsmith import Client

client = Client()

dataset = client.create_dataset("Skills: Trajectory", description="Trajectory evaluation")
client.create_examples(
    inputs=[ex["inputs"] for ex in examples],
    outputs=[ex["outputs"] for ex in examples],
    dataset_name="Skills: Trajectory",
)
```
