Bind different tools based on user role.

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

def get_model_with_tools(user_role: str):
    tools = [public_tool]

    if user_role == "admin":
        tools.append(admin_tool)

    return model.bind_tools(tools)

# Different users get different tools
admin_model = get_model_with_tools("admin")
user_model = get_model_with_tools("user")
```
