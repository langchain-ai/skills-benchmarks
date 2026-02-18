"""
SQL query agent with ReAct-style tool loop and LangSmith tracing.
Ground truth for validation - correctly traced version.
"""

import json
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

client = wrap_openai(OpenAI())

# Database path
DB_PATH = Path(__file__).parent.parent / "environment" / "backend" / "chinook.db"

# Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": "Get the database schema to understand table structures and relationships. Call this to understand what tables and columns are available.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql_query",
            "description": "Execute a SQL query against the Chinook database and return results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


@traceable(name="get_database_schema", run_type="tool")
def get_database_schema() -> str:
    """Get the database schema information."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_parts = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        col_info = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        schema_parts.append(f"- {table_name}: {col_info}")

    conn.close()
    return "Tables:\n" + "\n".join(schema_parts)


@traceable(name="execute_sql_query", run_type="tool")
def execute_sql_query(query: str) -> str:
    """Execute a SQL query and return results."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []

        # Format results as list of dicts
        formatted = [dict(zip(columns, row, strict=False)) for row in results[:20]]  # Limit to 20 rows
        return json.dumps(formatted, indent=2)
    except Exception as e:
        return f"SQL Error: {str(e)}"
    finally:
        conn.close()


@traceable(name="handle_tool_call")
def handle_tool_call(tool_name: str, tool_args: dict) -> str:
    """Execute a tool and return the result."""
    if tool_name == "get_database_schema":
        return get_database_schema()
    elif tool_name == "execute_sql_query":
        return execute_sql_query(tool_args.get("query", ""))
    else:
        return f"Unknown tool: {tool_name}"


@traceable(name="handle_query", run_type="chain")
def handle_query(question: str) -> str:
    """ReAct-style agent loop: reason about question, call tools, generate answer."""
    messages = [
        {
            "role": "system",
            "content": """You are a SQL expert assistant. Answer questions about the Chinook music database by:
1. First getting the schema to understand the tables
2. Writing and executing SQL queries to get the data
3. Providing a clear answer based on the results

Use the tools available to you. You may need to call multiple tools.""",
        },
        {"role": "user", "content": question},
    ]

    # Agent loop - keep going until no more tool calls
    max_iterations = 10
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        # If no tool calls, we have the final answer
        if not assistant_message.tool_calls:
            return assistant_message.content

        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Execute the tool
            result = handle_tool_call(tool_name, tool_args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return "Max iterations reached without final answer."


if __name__ == "__main__":
    test_questions = [
        "Which albums have the most tracks?",
        "Which 3 genres generated the most revenue?",
        "What are the most popular artists by number of tracks?",
    ]

    for question in test_questions:
        print(f"\n{'=' * 50}")
        print(f"Question: {question}")
        print(f"{'=' * 50}")
        answer = handle_query(question)
        print(f"Answer: {answer}")
