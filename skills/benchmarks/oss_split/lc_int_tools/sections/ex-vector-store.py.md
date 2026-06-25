Convert vector store retriever to agent tool.

```python
from langchain_core.tools import create_retriever_tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# Create vector store
vectorstore = InMemoryVectorStore.from_texts(
    ["LangChain is a framework...", "Agents use tools..."],
    embedding=OpenAIEmbeddings(),
)

# Convert to tool
retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="knowledge_base",
    description="Search the knowledge base for information about LangChain",
)

# Use in agent
from langchain.agents import create_agent

agent = create_agent(model="gpt-4.1", tools=[retriever_tool])
```
