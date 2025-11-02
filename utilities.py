import re
from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()


def query_extractor(llm_response: str) -> str:
    # Step 2: Extract SQL query from the response
    start = "```sql"
    end = "```"

    start_index = llm_response.find(start)
    end_index = llm_response.find(end, start_index + len(start))

    # Check if both delimiters are found and extract the substring between them
    if start_index != -1 and end_index != -1:
        res = llm_response[start_index + len(start):end_index]
        sql_query = res.strip()
        return sql_query
    else:
        raise ValueError("Delimiters not found")


def error_extractor(llm_response: str) -> str:
    # Step 2: Extract SQL query from the response
    start = "```error"
    end = "```"

    start_index = llm_response.find(start)
    end_index = llm_response.find(end, start_index + len(start))

    # Check if both delimiters are found and extract the substring between them
    if start_index != -1 and end_index != -1:
        res = llm_response[start_index + len(start):end_index]
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
            You are an SQL expert. 
            Convert the user's question into a valid PostgreSQL query. Only use SELECT statements.
            The response should only contain the SQL query without any explanations.
            Use following database schema to create the query:
            {db_schema}
            User: {user_question}
            SQL:
        """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_client = genai.Client(api_key=gemini_api_key)
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    print(response.text)
    return response.text.strip()
