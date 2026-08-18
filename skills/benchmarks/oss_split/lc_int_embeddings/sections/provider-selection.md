| Provider | Best For | Model Examples | Dimensions | Package (Python / TypeScript) | Key Features |
|----------|----------|----------------|------------|-------------------------------|--------------|
| **OpenAI** | General purpose, high quality | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | 1536, 3072 | `langchain-openai` / `@langchain/openai` | High quality, reliable, flexible dimensions |
| **Azure OpenAI** | Enterprise, compliance | text-embedding-ada-002 (Azure) | 1536 | `langchain-openai` / `@langchain/openai` | Enterprise SLAs, data residency |
| **Cohere** | Multilingual, search optimization | embed-english-v3.0, embed-multilingual-v3.0 | 1024 | `langchain-cohere` / `@langchain/cohere` | Search/clustering modes, multilingual |
| **HuggingFace** | Open source, customizable | all-MiniLM-L6-v2, BGE models | Varies | `langchain-huggingface` / `@langchain/community` | Free, local inference, many models |
| **Google** | GCP integration | textembedding-gecko | 768 | `langchain-google-genai` / `@langchain/google-genai` | GCP ecosystem, multimodal |
| **Ollama** | Local, privacy | llama2, mistral, nomic-embed-text | Varies | `langchain-ollama` / `@langchain/ollama` | Fully local, no API costs, privacy |
