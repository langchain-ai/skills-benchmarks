Common evaluation dataset types:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior.
- **trajectory** - Tool call sequence. Tests execution path.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
