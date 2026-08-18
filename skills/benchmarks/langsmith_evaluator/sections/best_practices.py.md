1. **Use structured output for LLM judges** - More reliable than parsing free-text
2. **Match evaluator to dataset type**
   - Final Response → LLM as Judge for quality
   - Trajectory → Custom Code for sequence
3. **Use async for LLM judges** - Enables parallel evaluation
4. **Test evaluators before uploading** - Run evaluator on sample inputs/outputs locally. Verify field names (e.g. `run["outputs"]["response"]`) match the actual dataset schema
