Use SQL database toolkit for queries.

```python
# SQL Database Toolkit
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///example.db")
toolkit = SQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()
# Includes: query, schema info, query checker, etc.

# Use in agent
agent = create_agent(model="gpt-4.1", tools=tools)
```
