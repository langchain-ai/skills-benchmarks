"""
SQL Analytics Agent for Chinook Music Store Database
Pre-built agent that generates traces in LangSmith for testing trace/dataset skills.
"""

import os
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# Database connection
DB_PATH = "chinook.db"


@tool
def execute_sql_query(query: str) -> str:
    """
    Execute a SELECT query on the Chinook music store database.

    Database Schema:
    - albums (AlbumId, Title, ArtistId)
    - artists (ArtistId, Name)
    - tracks (TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)
    - genres (GenreId, Name)
    - invoice_items (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
    - invoices (InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total)
    - customers (CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId)

    Args:
        query: SQL SELECT query to execute

    Returns:
        Query results as formatted string or error message
    """
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for security reasons."

    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    if any(keyword in query_upper for keyword in dangerous_keywords):
        return f"Error: Query contains forbidden keywords. Only SELECT queries are allowed."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()

        if not results:
            return "Query executed successfully but returned no results."

        formatted_results = []
        formatted_results.append(" | ".join(column_names))
        formatted_results.append("-" * (len(" | ".join(column_names))))
        for row in results:
            formatted_results.append(" | ".join(str(value) for value in row))
        return "\n".join(formatted_results)

    except sqlite3.Error as e:
        return f"SQL Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_database_schema() -> str:
    """
    Get the complete schema of the Chinook database including all tables and their columns.

    Returns:
        Formatted string with table names and their column definitions
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()

        schema_info = ["=== CHINOOK DATABASE SCHEMA ===\n"]
        for table in tables:
            table_name = table[0]
            schema_info.append(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                pk_marker = " [PRIMARY KEY]" if is_pk else ""
                schema_info.append(f"  - {col_name} ({col_type}){pk_marker}")
        conn.close()
        return "\n".join(schema_info)

    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


def create_sql_agent():
    """Create and return the SQL analytics agent."""
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_prompt = """You are a SQL analytics expert for the Chinook music store database.

Your role is to help users analyze data by:
1. Understanding their business questions
2. Exploring the database schema when needed
3. Writing efficient SQL queries with JOINs, GROUP BY, aggregations, and subqueries
4. Interpreting and explaining the results

Guidelines:
- Always check the schema first if you're unsure about table structures
- Write clear, well-formatted SQL queries
- Use appropriate JOINs to combine data from multiple tables
- Handle edge cases and provide meaningful error messages
- Explain your queries and results in business terms

Remember: Only SELECT queries are allowed for security."""

    tools = [execute_sql_query, get_database_schema]
    agent = create_agent(model, tools, system_prompt=system_prompt)
    return agent


def run_query(question: str) -> str:
    """Run a single query through the agent and return the response."""
    agent = create_sql_agent()
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    messages = result.get("messages", [])
    if messages:
        return messages[-1].content
    return "No response received from agent."


if __name__ == "__main__":
    # Run a few test queries to generate traces
    test_questions = [
        "Which 3 genres generated the most revenue?",
        "Who are the top 5 customers by total spending?",
        "What are the most popular artists by number of tracks?",
    ]

    print("=" * 80)
    print("SQL ANALYTICS AGENT - Generating Traces")
    print("=" * 80)

    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Query {i}/{len(test_questions)} ---")
        print(f"Question: {question}\n")
        try:
            response = run_query(question)
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"Error: {e}")
        print()

    print("=" * 80)
    print("Done - Traces should now be visible in LangSmith")
    print("=" * 80)
