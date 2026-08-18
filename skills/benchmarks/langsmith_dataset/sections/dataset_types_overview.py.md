Common evaluation dataset types:

- **final_response** - Full conversation with expected output. Tests complete agent behavior.
- **single_step** - Single node inputs/outputs. Tests specific node behavior. Use run name to target a node.
- **trajectory** - Tool call sequence. Tests execution path. Use depth to control extraction.
- **rag** - Question/chunks/answer/citations. Tests retrieval quality. Only matches `run_type="retriever"`.
