Related tools grouped as toolkit:

```python
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email message.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    return f"Email sent to {to}"

@tool
def read_emails(folder: str = "inbox", limit: int = 10) -> str:
    """Read emails from a folder.

    Args:
        folder: Email folder name (default: inbox)
        limit: Maximum emails to retrieve (default: 10)
    """
    return f"Retrieved {limit} emails from {folder}"

email_tools = [send_email, read_emails]

from langchain.agents import create_agent
agent = create_agent(model="gpt-4.1", tools=email_tools)
```
