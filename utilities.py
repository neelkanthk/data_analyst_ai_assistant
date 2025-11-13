import re
from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()


def query_extractor(text: str) -> str:
    # Step 2: Extract SQL query from the response
    start = "<sql>"
    end = "</sql>"

    start_index = text.find(start)
    end_index = text.find(end, start_index + len(start))

    # Check if both delimiters are found and extract the substring between them
    if start_index != -1 and end_index != -1:
        res = text[start_index + len(start):end_index]
        sql_query = res.strip()
        return sql_query
    else:
        raise ValueError("Delimiters not found")


def error_extractor(text: str) -> str:
    # Step 2: Extract SQL query from the response
    start = "```error"
    end = "```"

    start_index = text.find(start)
    end_index = text.find(end, start_index + len(start))

    # Check if both delimiters are found and extract the substring between them
    if start_index != -1 and end_index != -1:
        res = text[start_index + len(start):end_index]
        error_message = res.strip()
        return error_message
    else:
        raise ValueError("Delimiters not found")


def is_safe_sql(sql_query: str) -> bool:
    sql_query = sql_query.strip().lower()
    if not sql_query.startswith("select"):
        return False
    if re.search(r"\b(update|insert|delete|drop|alter|truncate)\b", sql_query):
        return False
    return True


def generate_sql_from_user_query(user_question: str, db_schema: str) -> str:

    # Load the schema JSON
    # with open("db_schema.json", "r", encoding="utf-8") as f:
    #     schema_json = json.load(f)

    # # Convert it back to a formatted JSON string
    # db_schema = json.dumps(schema_json, indent=2)
    prompt = f"""
            You are a highly intelligent SQL query generator. Your role is to:
            1. Analyze the natural language query carefully
            2. Understand the database schema structure
            3. Identify relevant tables, columns, and relationships
            4. Generate correct, optimized SQL queries
            5. Follow standard SQL syntax
            6. Only generate SQL queries that are safe to run (i.e., only SELECT statements)

            Key Guidelines:
            - Use only columns and tables present in the schema
            - Pay attention to data types and constraints
            - Consider foreign key relationships for joins
            - Optimize for performance when possible
            - Return only the SQL query without explanations

            Use following Database Schema to create the query:
            {db_schema}
            User Question in Natural Language: {user_question}
            SQL:
        """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_client = genai.Client(api_key=gemini_api_key)
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    print(response.text)
    return response.text.strip()
