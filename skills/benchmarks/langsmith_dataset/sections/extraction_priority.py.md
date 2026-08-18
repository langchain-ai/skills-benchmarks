When extracting inputs/outputs from traces for dataset creation, use this priority:

1. **User-specified fields** (custom extraction logic)
2. **Messages array** (LangChain/OpenAI format)
3. **Common fields** (inputs: query, input, question, message, prompt, text; outputs: answer, output, response, result)
4. **Raw dict** (fallback)
