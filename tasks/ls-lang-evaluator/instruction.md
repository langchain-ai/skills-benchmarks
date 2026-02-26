We've collected LangSmith datasets for each agent in this full-stack project:
- Backend SQL Agent: `{py_dataset}` (trajectory dataset)
- Frontend Support Bot: `{ts_dataset}` (final_response dataset)

Create evaluators to score the agents. These evaluators will be attached to the LangSmith datasets, so they have a dependency on the datasets structure.

1. For the backend SQL agent (`backend/sql_agent.py`):
   - Create a trajectory evaluator that compares the tool calls made by the agent to the expected_trajectory in the dataset.
   - The evaluator should be named `evaluator` with an appropriate file extension.
   - Upload the evaluator to the LangSmith dataset with name `bench-be-{run_id}`.

2. For the frontend support bot (`frontend/support_bot.ts`):
   - Create a final_response evaluator that checks if the answer from our bot matches the expected response in the dataset exactly.
   - The evaluator should be named `evaluator` with an appropriate file extension.
   - Upload the evaluator to the LangSmith dataset with name `bench-fe-{run_id}`.
